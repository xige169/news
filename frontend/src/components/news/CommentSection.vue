<template>
  <section class="comments">
    <header class="comments__header">
      <h2 class="comments__title">{{ t('comments.title') }}</h2>
      <span class="comments__count" v-if="total">{{ total }}</span>
    </header>

    <div class="comments__composer">
      <n-input
        v-model:value="draft"
        type="textarea"
        :placeholder="auth.isLoggedIn ? t('comments.placeholder') : t('comments.loginRequired')"
        :autosize="{ minRows: 3, maxRows: 6 }"
        :maxlength="1000"
        show-count
        :disabled="!auth.isLoggedIn || submitting"
      />
      <div class="comments__composer-actions">
        <n-button
          type="primary"
          :loading="submitting"
          :disabled="!draft.trim() || submitting"
          @click="onSubmit"
        >
          {{ t('comments.publish') }}
        </n-button>
      </div>
    </div>

    <div v-if="loading && !items.length" class="comments__loading">
      <LoadingSkeleton variant="card" />
    </div>

    <ul v-else-if="items.length" class="comments__list">
      <CommentItem
        v-for="item in items"
        :key="item.id"
        :comment="item"
        :current-user-id="currentUserId"
        :news-id="newsId"
        :depth="0"
        @reply="onReply"
        @delete="onDelete"
        @like="onLike"
      />
    </ul>

    <p v-else class="comments__empty">{{ t('comments.empty') }}</p>

    <div v-if="hasMore" class="comments__more">
      <n-button :loading="loadingMore" @click="loadMore">{{ t('comments.loadMore') }}</n-button>
    </div>

    <n-modal v-model:show="showLoginModal" preset="card" :title="t('comments.loginPromptTitle')" style="width: 360px">
      <p class="comments__modal-text">{{ t('comments.loginPromptText') }}</p>
      <template #footer>
        <div class="comments__modal-actions">
          <n-button @click="showLoginModal = false">{{ t('comments.cancel') }}</n-button>
          <n-button type="primary" @click="goLogin">{{ t('comments.goLogin') }}</n-button>
        </div>
      </template>
    </n-modal>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { NButton, NInput, NModal, useMessage } from 'naive-ui'

import LoadingSkeleton from '../feedback/LoadingSkeleton.vue'
import CommentItem from './CommentItem.vue'
import {
  fetchComments,
  postComment,
  deleteComment,
  likeComment
} from '../../services/comments'
import { useAuthStore } from '../../store/auth'

const props = defineProps({
  newsId: { type: Number, required: true }
})

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const message = useMessage()
const { t } = useI18n()

const items = ref([])
const total = ref(0)
const hasMore = ref(false)
const page = ref(1)
const pageSize = 20

const loading = ref(false)
const loadingMore = ref(false)
const submitting = ref(false)
const draft = ref('')
const showLoginModal = ref(false)

const currentUserId = computed(() => auth.userInfo?.id ?? null)

const load = async ({ append = false } = {}) => {
  if (append) {
    loadingMore.value = true
  } else {
    loading.value = true
    page.value = 1
  }
  try {
    const data = await fetchComments({
      newsId: props.newsId,
      page: page.value,
      pageSize
    })
    const list = data?.list || []
    items.value = append ? [...items.value, ...list] : list
    total.value = data?.total || 0
    hasMore.value = Boolean(data?.hasMore)
  } catch (err) {
    message.error(err?.message || t('comments.loadFailed'))
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const loadMore = async () => {
  page.value += 1
  await load({ append: true })
}

const onSubmit = async () => {
  if (!auth.isLoggedIn) {
    showLoginModal.value = true
    return
  }
  const content = draft.value.trim()
  if (!content) return
  submitting.value = true
  try {
    const created = await postComment({ newsId: props.newsId, content })
    items.value = [{ ...created, replies: [] }, ...items.value]
    total.value += 1
    draft.value = ''
    message.success(t('comments.publishedSuccess'))
  } catch (err) {
    message.error(err?.message || t('comments.publishFailed'))
  } finally {
    submitting.value = false
  }
}

const findAndUpdate = (list, commentId, updater) => {
  for (const node of list) {
    if (node.id === commentId) {
      updater(node)
      return true
    }
    if (node.replies?.length && findAndUpdate(node.replies, commentId, updater)) {
      return true
    }
  }
  return false
}

const onReply = async ({ parentId, content }) => {
  if (!auth.isLoggedIn) {
    showLoginModal.value = true
    return
  }
  try {
    const created = await postComment({ newsId: props.newsId, content, parentId })
    findAndUpdate(items.value, parentId, (node) => {
      node.replies = [...(node.replies || []), { ...created, replies: [] }]
    })
    message.success(t('comments.publishedSuccess'))
  } catch (err) {
    message.error(err?.message || t('comments.publishFailed'))
  }
}

const onDelete = async (commentId) => {
  try {
    await deleteComment(commentId)
    findAndUpdate(items.value, commentId, (node) => {
      node.isDeleted = true
      node.content = ''
      node.userId = null
      node.userName = null
      node.userAvatar = null
    })
    message.success(t('comments.deletedSuccess'))
  } catch (err) {
    message.error(err?.message || t('comments.deleteFailed'))
  }
}

const onLike = async ({ commentId, like }) => {
  if (!auth.isLoggedIn) {
    showLoginModal.value = true
    return
  }
  try {
    const data = await likeComment({ commentId, like })
    findAndUpdate(items.value, commentId, (node) => {
      node.liked = data.liked
      node.likeCount = data.likeCount
    })
  } catch (err) {
    message.error(err?.message || t('comments.likeFailed'))
  }
}

const goLogin = () => {
  showLoginModal.value = false
  router.push({ path: '/login', query: { redirect: route.fullPath } })
}

watch(() => props.newsId, () => {
  if (Number.isFinite(props.newsId)) {
    load()
  }
})

onMounted(() => {
  if (Number.isFinite(props.newsId)) {
    load()
  }
})
</script>

<style scoped>
.comments {
  max-width: 760px;
  margin: var(--sp-12) auto 0;
  padding-top: var(--sp-8);
  border-top: 1px solid var(--border);
}

.comments__header {
  display: flex;
  align-items: baseline;
  gap: var(--sp-3);
  margin-bottom: var(--sp-6);
  padding-bottom: var(--sp-3);
  border-bottom: 2px solid var(--text-primary);
}

.comments__title {
  font-family: var(--font-serif);
  font-size: var(--fs-24);
  font-weight: 800;
}

.comments__count {
  color: var(--text-muted);
  font-size: var(--fs-14);
}

.comments__composer {
  margin-bottom: var(--sp-8);
}

.comments__composer-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--sp-3);
}

.comments__list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--sp-5);
}

.comments__empty {
  color: var(--text-muted);
  text-align: center;
  padding: var(--sp-8) 0;
}

.comments__more {
  display: flex;
  justify-content: center;
  margin-top: var(--sp-6);
}

.comments__loading {
  padding: var(--sp-4) 0;
}

.comments__modal-text {
  font-size: var(--fs-14);
  color: var(--text-secondary);
  line-height: var(--lh-normal);
}

.comments__modal-actions {
  display: flex;
  gap: var(--sp-2);
  justify-content: flex-end;
}
</style>
