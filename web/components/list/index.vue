<template>
    <div v-auto-animate :class="['results', { group }]">
        <list-item
            v-for="(item, index) in items"
            :key="index"
            :name="getName(item)"
            class="card"
            :to="linkBuilder && linkBuilder(item)"
            :color="itemColor"
            @click="
                () => {
                    if (onItemClick) {
                        onItemClick(item);
                    }
                }
            "
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
