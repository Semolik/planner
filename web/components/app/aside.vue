<template>
    <aside>
        <slot name="top" />
        <div class="aside-block" v-for="(block, index) in blocks" :key="index">
            <div class="block-name" v-if="block.name">{{ block.name }}</div>
            <div class="items">
                <nuxt-link
                    class="aside-item"
                    v-for="item in block.items"
                    :key="item.path"
                    :to="{
                        name: item.path,
                    }"
                >
                    <Icon :name="item.icon" />
                    <span>
                        {{ item.name }}
                    </span>
                </nuxt-link>
            </div>
        </div>
        <slot name="bottom" />
    </aside>
</template>
<script setup>
const { blocks } = defineProps({
    blocks: {
        type: Array,
        default: () => [],
    },
});
const mounted = ref(false);
onMounted(() => {
    mounted.value = true;
});
</script>
<style lang="scss" scoped>
aside {
    display: flex;
    flex-direction: column;
    width: 280px;

    border-right: 1px solid $border-color;
    height: 100%;
    padding: 5px;

    .spliter {
        height: 1px;
        background-color: $border-color;
    }
    .aside-block {
        padding: 8px;
        display: flex;
        flex-direction: column;
        gap: 10px;

        .items {
            display: flex;
            flex-direction: column;
            gap: 5px;
            .aside-item {
                display: flex;
                padding: 10px;
                text-decoration: none;
                align-items: center;
                gap: 10px;
                border-radius: 10px;
                color: $text-color-secondary;

                &.router-link-exact-active {
                    color: $text-color;
                    background-color: rgba(0, 0, 0, 0.05);
                }

                .iconify {
                    width: 20px;
                    height: 20px;
                    color: $text-color-secondary;
                }
                .name {
                    color: $text-color-secondary;
                    margin-bottom: 10px;
                    word-wrap: break-word;
                    overflow-wrap: anywhere;
                }
            }
        }
    }
    @include sm(true) {
        & {
            width: 100%;
            padding: 5px;
        }
    }
}
</style>
