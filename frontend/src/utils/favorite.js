export const getFavoriteActionMeta = (isFavorite, loading) => {
  if (loading) {
    return {
      icon: isFavorite ? 'star' : 'star-o',
      label: '处理中',
      pressed: Boolean(isFavorite)
    }
  }

  return {
    icon: isFavorite ? 'star' : 'star-o',
    label: isFavorite ? '已收藏' : '收藏',
    pressed: Boolean(isFavorite)
  }
}
