export const resetPaginationState = () => ({
  items: [],
  page: 1,
  hasMore: true
})

export const mergeNewsPage = (state, items, hasMore, page) => ({
  items: page === 1 ? items : [...state.items, ...items],
  page,
  hasMore
})
