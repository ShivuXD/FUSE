package controller

import (
    "context"
    "testing"
    batch "k8s.io/api/batch/v1"
    core "k8s.io/api/core/v1"
    "k8s.io/apimachinery/pkg/runtime"
    "k8s.io/apimachinery/pkg/types"
    ctrl "sigs.k8s.io/controller-runtime"
    "sigs.k8s.io/controller-runtime/pkg/client/fake"
)

func TestReconcileBlocksMissingPlan(t *testing.T) {
    scheme := runtime.NewScheme()
    scan := scanObject()
    scan.SetName("test")
    scan.SetNamespace("test")
    scheme.AddKnownTypeWithName(GVK, scanObject())
    c := fake.NewClientBuilder().WithScheme(scheme).WithStatusSubresource(scan).WithObjects(scan).Build()
    reconciler := &Reconciler{Client: c, Scheme: scheme, Image: "example@sha256:digest"}
    _, err := reconciler.Reconcile(context.Background(), ctrl.Request{NamespacedName: types.NamespacedName{Name: "test", Namespace: "test"}})
    if err != nil { t.Fatal(err) }
    updated := scanObject()
    if err := c.Get(context.Background(), types.NamespacedName{Name: "test", Namespace: "test"}, updated); err != nil { t.Fatal(err) }
    status := updated.Object["status"].(map[string]interface{})
    if status["phase"] != "Blocked" { t.Fatal(status) }
}

func TestWorkerIsolation(t *testing.T) {
    job := BuildJob("probe", "test", "example@sha256:digest", 1000, 512, 30)
    pod := job.Spec.Template.Spec
    container := pod.Containers[0]
    if *pod.AutomountServiceAccountToken || !*pod.SecurityContext.RunAsNonRoot ||
        *container.SecurityContext.AllowPrivilegeEscalation || !*container.SecurityContext.ReadOnlyRootFilesystem ||
        container.SecurityContext.Capabilities.Drop[0] != "ALL" || *job.Spec.ActiveDeadlineSeconds != 30 ||
        len(container.Resources.Limits) != 2 || pod.HostNetwork || len(pod.Volumes) != 1 {
        t.Fatal("worker isolation regressed")
    }
}

func TestJobFailuresRemainOperational(t *testing.T) {
    for _, reason := range []string{"DeadlineExceeded", "OOMKilled", "PodFailurePolicy", "BackoffLimitExceeded"} {
        job := &batch.Job{Status: batch.JobStatus{Conditions: []batch.JobCondition{{
            Type: batch.JobFailed, Status: core.ConditionTrue, Reason: reason,
        }}}}
        phase, detail := JobPhase(job)
        if phase != "Failed" || detail != reason { t.Fatalf("%s: %s %s", reason, phase, detail) }
    }
    phase, _ := JobPhase(&batch.Job{})
    if phase != "Pending" { t.Fatal("missing image must not imply successful analysis") }
}
