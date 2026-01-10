#!/bin/bash
#
# GenAIOps Lab Installation Script
# Deploys the AI501 lab environment on OpenShift
#

set -e

NAMESPACE="ai501"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

#------------------------------------------------------------------------------
# Helper Functions
#------------------------------------------------------------------------------

log_step() {
    echo ""
    echo "============================================================"
    echo "$1"
    echo "============================================================"
}

log_info() {
    echo "[INFO] $1"
}

#------------------------------------------------------------------------------
# Step 1: Install Operators
#------------------------------------------------------------------------------

log_step "Step 1/6: Installing operators"
helm upgrade --install ai501-base operators \
    --namespace "${NAMESPACE}" \
    --create-namespace

log_info "Waiting for GitOps operator to be ready..."
oc wait --for=jsonpath='{.status.availableReplicas}'=1 \
    -n openshift-gitops deployment/cluster

#------------------------------------------------------------------------------
# Step 2: Install Shared Toolings
#------------------------------------------------------------------------------

log_step "Step 2/6: Installing shared toolings"
helm upgrade --install ai501-toolings toolings \
    --namespace "${NAMESPACE}" \
    --create-namespace

#------------------------------------------------------------------------------
# Step 3: Install Student Content
#------------------------------------------------------------------------------

log_step "Step 3/6: Installing student content"
helm upgrade --install ai501-student-content student-content \
    --namespace "${NAMESPACE}" \
    --create-namespace

#------------------------------------------------------------------------------
# Step 4: Configure Authentication
#------------------------------------------------------------------------------

log_step "Step 4/6: Configuring OAuth with HTPasswd"
oc patch --type=merge OAuth/cluster -p '{
    "spec": {
        "identityProviders": [{
            "name": "Students",
            "type": "HTPasswd",
            "mappingMethod": "claim",
            "htpasswd": {
                "fileData": {
                    "name": "htpasswd-ai501"
                }
            }
        }]
    }
}'

#------------------------------------------------------------------------------
# Step 5: Configure ArgoCD for Multi-Tenancy
#------------------------------------------------------------------------------

log_step "Step 5/6: Configuring ArgoCD for cluster-wide access"

attendees=$(grep attendees "${SCRIPT_DIR}/student-content/values.yaml" | cut -d':' -f2 | tr -d ' ')

# Build namespace list for ArgoCD
NS=""
for ((i=1; i<=attendees; i++)); do
    if [ $i -eq 1 ]; then
        NS="user${i}-toolings"
    else
        NS="${NS},user${i}-toolings"
    fi
done

log_info "Enabling ArgoCD for namespaces: ${NS}"
oc -n openshift-gitops-operator patch subscriptions.operators.coreos.com/openshift-gitops-operator \
    --type=json \
    -p '[
        {
            "op": "add",
            "path": "/spec/config/env",
            "value": [{"name": "DISABLE_DEFAULT_ARGOCD_INSTANCE", "value": "true"}]
        },
        {
            "op": "add",
            "path": "/spec/config/env/1",
            "value": {"name": "ARGOCD_CLUSTER_CONFIG_NAMESPACES", "value": "'"${NS}"'"}
        }
    ]'

#------------------------------------------------------------------------------
# Step 6: Configure Tekton and Monitoring
#------------------------------------------------------------------------------

log_step "Step 6/6: Configuring Tekton and user workload monitoring"

log_info "Disabling Tekton affinity assistant for cost optimization..."
oc patch tektonconfig config --type merge -p '{"spec":{"pipeline":{"disable-affinity-assistant":true}}}'
oc patch configmap feature-flags -n openshift-pipelines --type merge \
    -p '{"data":{"disable-affinity-assistant":"true","coschedule":"disabled"}}'
oc patch configmap config-defaults -n openshift-pipelines --type merge \
    -p '{"data":{"default-affinity-assistant-pod-template":"","default-pod-template":""}}'

log_info "Restarting Tekton controller to apply changes..."
oc delete pod -l app=tekton-pipelines-controller -n openshift-pipelines

log_info "Configuring user workload monitoring..."
oc -n openshift-user-workload-monitoring patch configmap user-workload-monitoring-config \
    --type=merge \
    -p '{"data": {"config.yaml": "prometheus:\n  logLevel: debug\n  retention: 15d\nalertmanager:\n  enabled: true\n  enableAlertmanagerConfig: true\n"}}'

#------------------------------------------------------------------------------
# Complete
#------------------------------------------------------------------------------

log_step "Installation Complete"
echo ""
echo "Next steps:"
echo "  1. Verify operators: oc get csv -n openshift-operators"
echo "  2. Check pods:       oc get pods -n ${NAMESPACE}"
echo "  3. List namespaces:  oc get namespaces | grep user"
echo ""
