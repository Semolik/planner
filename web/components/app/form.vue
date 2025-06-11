<template>
    <div :class="['form-container', { 'full-height': fullHeight }]">
        <div class="form-top">
            <slot name="top"></slot>
        </div>
        <div class="form-wrapper">
            <form class="form" v-bind="$attrs" @submit.prevent="emit('submit')">
                <div class="headline" v-if="headline">
                    <div class="headline-text">
                        {{ headline }}
                    </div>
                    <slot name="headline"></slot>
                    <div class="headline-md">
                        <slot name="headline-md"></slot>
                    </div>
                </div>
                <div class="description" v-if="description">
                    {{ description }}
                </div>
                <slot></slot>
            </form>
            <div class="bottom-form"><slot name="bottom"></slot></div>
        </div>
    </div>
</template>
<script setup>
defineProps({
    headline: String,
    description: String,
    maxWidth: {
        type: String,
        default: "400px",
    },
    fullHeight: Boolean,
});
const emit = defineEmits(["submit"]);
</script>
<style scoped lang="scss">
.form-container {
    flex-direction: column;
    gap: 10px;
    width: 100%;

    &.full-height {
        height: 100%;
        min-height: min-content;

        .form-wrapper {
            height: 100%;
            min-height: min-content;
        }
    }
    .form-top:empty {
        display: none;
    }
    .form-top,
    .form-wrapper {
        padding: 10px;
        @include md(true) {
            & {
                padding: 10px;
            }
        }
    }
    .form-wrapper {
        display: flex;
        flex-direction: column;
        gap: 10px;
        width: 100%;

        @include sm(true) {
            & {
                padding: 0;
            }
        }
        & {
            @include flex-center;
        }
    }
    .bottom-form {
        max-width: v-bind(maxWidth);
        width: 100%;
        display: flex;
        flex-direction: column;
    }

    .form {
        color: $text-color;
        width: 100%;
        max-width: v-bind(maxWidth);

        padding: 20px;
        display: flex;
        flex-direction: column;
        gap: 10px;
        position: relative;
        background-color: $secondary-bg;
        border-radius: 20px;
        border: 1px solid $border-color;
        position: relative;

        .description {
            font-size: 14px;
            color: $text-color-secondary;
            margin-bottom: 10px;
        }
        .headline {
            font-size: 20px;
            text-align: center;
            display: flex;
            align-items: center;
            gap: 8px;
            .headline-text {
                flex-grow: 1;
            }
            @include sm(true) {
                & {
                    margin-bottom: 20px;
                }
            }
        }
        .headline-md {
            display: contents;
            @include md(true) {
                & {
                    display: none;
                }
            }
        }
    }
}
</style>
