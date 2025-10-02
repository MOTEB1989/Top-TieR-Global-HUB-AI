{{- define "runner-service.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "runner-service.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name (include "runner-service.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "runner-service.labels" -}}
helm.sh/chart: {{ include "runner-service.chart" . }}
{{ include "runner-service.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "runner-service.selectorLabels" -}}
app.kubernetes.io/name: {{ include "runner-service.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "runner-service.chart" -}}
{{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{- end -}}

{{- define "runner-service.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{- default (include "runner-service.fullname" .) .Values.serviceAccount.name -}}
{{- else -}}
{{- default "default" .Values.serviceAccount.name -}}
{{- end -}}
{{- end -}}
