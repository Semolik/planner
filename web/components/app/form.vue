<template>
    <div
        :class="[
            'form-container',
            { 'full-height': fullHeight },
            { 'no-padding': noPadding },
            { 'center-mobile': centerMobile },
        ]"
    >
        <div class="form-top">
            <slot name="top"/>
        </div>
        <div class="form-wrapper">
            <form class="form" v-bind="$attrs" @submit.prevent="emit('submit')">
                <div v-if="headline" class="headline">
                    <div class="headline-text">
                        {{ headline }}
                    </div>
                    <slot name="headline"/>
                    <div class="headline-md">
                        <slot name="headline-md"/>
                    </div>
                </div>
                <div v-if="description" class="description">
                    {{ description }}
                </div>
                <slot/>
            </form>
            <div class="bottom-form"><slot name="bottom"/></div>
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
    noPadding: {
        type: Boolean,
        default: false,
    },
    centerMobile: {
        type: Boolean,
        required: false,
    },
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
        &.center-mobile .form-wrapper {
            justify-content: center;
        }
        @include md(true) {
            .form {
                height: 100%;
            }
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

        @include lg(true) {
            & {
                padding: 0;
            }
        }
        @include lg {
            & {
                @include flex-center;
            }
        }
    }
    .bottom-form {
        width: 100%;
        display: flex;
        flex-direction: column;
        @include lg {
            max-width: v-bind(maxWidth);
        }
    }
    &.no-padding {
        .form {
            padding: 0;
        }
    }
    .form {
        color: $text-color;
        width: 100%;

        display: flex;
        flex-direction: column;
        gap: 5px;
        position: relative;
        padding: 10px;
        @include lg {
            background-color: $secondary-bg;
            border: 1px solid $border-color;
            border-radius: 20px;
            padding: 20px;
            gap: 10px;
            max-width: v-bind(maxWidth);
        }
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
