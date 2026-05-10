<template>
  <li class="comment-item" :class="{ 'comment-item--deleted': comment.isDeleted }">
    <div class="comment-item__row">
      <img
        v-if="!comment.isDeleted && comment.userAvatar"
        :src="comment.userAvatar"
        :alt="comment.userName || ''"
        class="comment-item__avatar"
      />
      <div v-else class="comment-item__avatar comment-item__avatar--placeholder" />

      <div class="comment-item__main">
        <div class="comment-item__meta">
          <span class="comment-item__author">
            {{ comment.isDeleted ? t('comments.deletedAuthor') : (comment.userName || t('comments.anonymous')) }}
          </span>
          <span class="comment-item__time">{{ relativeTime }}</span>
        </div>

        <p class="comment-item__content">
          {{ comment.isDeleted ? t('comments.deleted') : comment.content }}
        </p>

        <div v-if="!comment.isDeleted" class="comment-item__actions">
          <button
            type="button"
            class="comment-item__action"
            :class="{ 'comment-item__action--active': comment.liked }"
            @click="toggleLike"
          >
            {{ comment.liked ? '♥' : '♡' }}
            <span v-if="comment.likeCount > 0">{{ comment.likeCount }}</span>
            <span v-else>{{ t('comments.like') }}</span>
          </button>
          <button type="button" class="comment-item__action" @click="showReply = !showReply">
            {{ t('comments.reply') }}
          </button>
          <button
            v-if="canDelete"
            type="button"
            class="comment-item__action comment-item__action--danger"
            @click="$emit('delete', comment.id)"
          >
            {{ t('comments.delete') }}
          </button>
        </div>

        <div v-if="showReply" class="comment-item__reply-box">
          <n-input
            v-model:value="replyDraft"
            type="textarea"
            :autosize="{ minRows: 2, maxRows: 4 }"
            :placeholder="t('comments.replyPlaceholder', { name: comment.userName || '' })"
            :maxlength="1000"
            show-count
          />
          <div class="comment-item__reply-actions">
            <n-button size="small" @click="cancelReply">{{ t('comments.cancel') }}</n-button>
            <n-button
              size="small"
              type="primary"
              :disabled="!replyDraft.trim()"
              @click="submitReply"
            >
              {{ t('comments.publish') }}
            </n-button>
          </div>
        </div>

        <ul v-if="comment.replies?.length" class="comment-item__replies">
          <CommentItem
            v-for="child in comment.replies"
            :key="child.id"
            :comment="child"
            :current-user-id="currentUserId"
            :news-id="newsId"
            :depth="depth + 1"
            @reply="(payload) => $emit('reply', payload)"
            @delete="(id) => $emit('delete', id)"
            @like="(payload) => $emit('like', payload)"
          />
        </ul>
      </div>
    </div>
  </li>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { NButton, NInput } from 'naive-ui'

const props = defineProps({
  comment: { type: Object, required: true },
  currentUserId: { type: Number, default: null },
  newsId: { type: Number, required: true },
  depth: { type: Number, default: 0 }
})

const emit = defineEmits(['reply', 'delete', 'like'])

const { t } = useI18n()
const showReply = ref(false)
const replyDraft = ref('')

const canDelete = computed(() => {
  return props.currentUserId != null && props.comment.userId === props.currentUserId
})

const relativeTime = computed(() => {
  const ts = props.comment.createdAt
  if (!ts) return ''
  const date = new Date(ts)
  if (Number.isNaN(date.getTime())) return ''
  const diff = (Date.now() - date.getTime()) / 1000
  if (diff < 60) return t('comments.timeJustNow')
  if (diff < 3600) return t('comments.timeMinutes', { n: Math.floor(diff / 60) })
  if (diff < 86400) return t('comments.timeHours', { n: Math.floor(diff / 3600) })
  if (diff < 86400 * 30) return t('comments.timeDays', { n: Math.floor(diff / 86400) })
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
})

const toggleLike = () => {
  emit('like', { commentId: props.comment.id, like: !props.comment.liked })
}

const cancelReply = () => {
  showReply.value = false
  replyDraft.value = ''
}

const submitReply = () => {
  const content = replyDraft.value.trim()
  if (!content) return
  emit('reply', { parentId: props.comment.id, content })
  cancelReply()
}
</script>

<style scoped>
.comment-item {
  list-style: none;
}

.comment-item__row {
  display: flex;
  gap: var(--sp-3);
}

.comment-item__avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  flex-shrink: 0;
  object-fit: cover;
}

.comment-item__avatar--placeholder {
  background: var(--bg-muted, #ddd);
}

.comment-item__main {
  flex: 1;
  min-width: 0;
}

.comment-item__meta {
  display: flex;
  align-items: baseline;
  gap: var(--sp-3);
  margin-bottom: var(--sp-1);
}

.comment-item__author {
  font-weight: 600;
  font-size: var(--fs-14);
}

.comment-item__time {
  color: var(--text-muted);
  font-size: var(--fs-12);
}

.comment-item__content {
  font-size: var(--fs-15);
  line-height: var(--lh-normal);
  color: var(--text-primary);
  white-space: pre-wrap;
  word-wrap: break-word;
}

.comment-item--deleted .comment-item__content {
  color: var(--text-muted);
  font-style: italic;
}

.comment-item__actions {
  display: flex;
  gap: var(--sp-4);
  margin-top: var(--sp-2);
}

.comment-item__action {
  border: 0;
  background: transparent;
  color: var(--text-muted);
  font-size: var(--fs-13);
  cursor: pointer;
  padding: 0;
  display: inline-flex;
  align-items: center;
  gap: var(--sp-1);
}

.comment-item__action:hover {
  color: var(--accent);
}

.comment-item__action--active {
  color: var(--accent);
}

.comment-item__action--danger:hover {
  color: #d83a3a;
}

.comment-item__reply-box {
  margin-top: var(--sp-3);
}

.comment-item__reply-actions {
  display: flex;
  gap: var(--sp-2);
  justify-content: flex-end;
  margin-top: var(--sp-2);
}

.comment-item__replies {
  list-style: none;
  padding: 0;
  margin: var(--sp-4) 0 0;
  display: flex;
  flex-direction: column;
  gap: var(--sp-4);
  padding-left: var(--sp-4);
  border-left: 2px solid var(--border);
}
</style>
