const DEFAULT_NEWS_IMAGE = 'https://picsum.photos/seed/news-cover/960/540'
const DEFAULT_AVATAR = 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg'

export const getNewsImageUrl = (value) => value || DEFAULT_NEWS_IMAGE

export const getAvatarUrl = (value) => value || DEFAULT_AVATAR
