<template>
    <div :class="['results', { group }]" v-auto-animate>
        <list-item
            v-for="(item, index) in items"
            :key="index"
            :name="getName(item)"
            class="card"
            :to="linkBuilder && linkBuilder(item)"
            @click="
                () => {
                    if (onItemClick) {
                        onItemClick(item);
                    }
                }
            "
            :color="itemColor"
        >
            <template #prepend>
                <slot name="prepend" :item="item" />
            </template>
            <template #item>
                <slot name="item" :item="item" />
            </template>
        </list-item>

        <div v-if="!items.length" class="empty-results">
            <div class="text-lg text-gray-500">Ничего не найдено</div>
        </div>
    </div>
</template>
<script setup>
import { routesNames } from "@typed-router";
defineProps({
    items: {
        type: Array,
        default: () => [],
    },
    getName: {
        type: Function,
        default: (item) => item.name,
    },
    linkBuilder: {
        type: Function,
        default: null,
    },
    onItemClick: {
        type: Function,
        default: null,
    },
    group: {
        type: Boolean,
        default: false,
    },
    itemColor: {
        type: String,
    },
});
</script>
<style scoped lang="scss">
.results {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 10px;

    height: 100%;

    .empty-results {
        height: 100%;
        grid-column: 1 / -1;
        grid-row: 1 / -1;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    &.group {
        @include md(true) {
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        }
    }
}
</style>
