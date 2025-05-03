<template>
    <nuxt-link :to="to" class="card">
        <div class="name">
            <slot name="prepend" />
            <div class="name-text">
                {{ name }}
            </div>
        </div>
        <slot name="item" />
    </nuxt-link>
</template>
<script setup>
defineProps({
    to: {
        type: Object,
        default: () => ({}),
    },
    name: {
        type: String,
        default: "",
    },
    color: {
        type: String,
        default: "white",
    },
});
</script>
<style scoped lang="scss">
.card {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    padding: 20px;
    border-radius: 10px;
    background-color: v-bind(color);
    border: 1px solid $border-color;

    .name {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-grow: 1;
        justify-content: center;
    }

    &:hover {
        border-color: black;
    }
    @include md(true) {
        justify-content: center;
        text-align: center;
        padding: 10px;
        .events-count {
            display: none;
        }
    }
}
</style>
