type ValidationDetail = {
  loc?: Array<string | number>
  msg?: string
}

const fieldLabelMap: Record<string, string> = {
  username: '用户名',
  password: '密码',
  display_name: '显示名称',
  email: '邮箱',
  body: '',
}

const messageMap: Record<string, string> = {
  'Field required': '该字段不能为空',
  'value is not a valid email address': '邮箱格式不正确',
  'Input should be a valid email address': '邮箱格式不正确',
  'String should have at least 1 character': '该字段不能为空',
}

function formatValidationItem(item: ValidationDetail) {
  const loc = (item.loc || []).map((part) => String(part))
  const fieldKey = [...loc].reverse().find((part) => fieldLabelMap[part] !== undefined) || ''
  const fieldLabel = fieldLabelMap[fieldKey] || fieldKey
  const message = messageMap[item.msg || ''] || item.msg || '输入不合法'
  return fieldLabel ? `${fieldLabel}：${message}` : message
}

export function getApiErrorMessage(error: any, fallback = '操作失败') {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string' && detail.trim()) {
    return detail
  }
  if (Array.isArray(detail) && detail.length > 0) {
    return detail.map((item) => formatValidationItem(item)).join('；')
  }
  if (typeof error?.response?.data?.message === 'string' && error.response.data.message.trim()) {
    return error.response.data.message
  }
  if (typeof error?.message === 'string' && error.message.trim()) {
    return error.message
  }
  return fallback
}
