<template>
    <nuxt-link class="user-card" :to="`/users/${user.id}`">
        <UAvatar
            :src="user.image"
            icon="material-symbols:image"
            :ui="{
                root: 'size-40 text-2xl avatar lg:size-36 md:size-32 sm:size-28',
            }"
        />
        <div class="field">
            {{ user.name }}
        </div>
        <slot />
    </nuxt-link>
</template>
<script setup>
defineProps({
    user: {
        type: Object,
        required: true,
    },
});
</script>
<style scoped lang="scss">
.user-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    padding: 10px;
    border: 1px solid $border-color;
    border-radius: 20px;

    &:hover {
        border-color: black;
    }

    .field {
        font-size: 16px;
        color: $text-color;
        text-align: center;
        word-break: break-word;
        @include clip-text(2);
        margin-bottom: auto;
    }
}
</style>
