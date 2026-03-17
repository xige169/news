export const GENDER_OPTIONS = [
  { label: '未设置', value: 'unknown' },
  { label: '男', value: 'male' },
  { label: '女', value: 'female' }
]

export const normalizeGender = (value) => {
  if (GENDER_OPTIONS.some((item) => item.value === value)) {
    return value
  }

  return 'unknown'
}

export const toGenderLabel = (value) => {
  return GENDER_OPTIONS.find((item) => item.value === value)?.label || '未设置'
}
