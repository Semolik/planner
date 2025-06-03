<template>
    <nuxt-link
        v-if="to"
        :to="to"
        :type="type"
        :class="[
            'app-button',
            { active: active },
            { min: min },
            { light: light },
            { red },
            { outline: outline },
        ]"
        v-bind="$attrs"
    >
        <div :class="['button-content', { loading: loading }]">
            <slot />
        </div>

        <div
            v-if="withLoader"
            :class="['loader-container', { active: loading }]"
        >
            <Icon name="svg-spinners:180-ring-with-bg" />
        </div>
    </nuxt-link>
    <button
        v-else
        :class="[
            'app-button',
            { active: active },
            { min: min },
            { light: light },
            { red },
            { outline: outline },
        ]"
        :type="type"
        v-bind="$attrs"
    >
        <div :class="['button-content', { loading: loading }]">
            <slot />
        </div>

        <div
            v-if="withLoader"
            :class="['loader-container', { active: loading }]"
        >
            <Icon name="svg-spinners:180-ring-with-bg" />
        </div>
    </button>
</template>
<script setup>
defineProps({
    active: {
        type: Boolean,
        default: false,
    },
    as: {
        type: String,
        default: "button",
    },
    red: {
        type: Boolean,
        default: false,
    },
    min: {
        type: Boolean,
        default: false,
    },
    light: {
        type: Boolean,
        default: false,
    },
    withLoader: {
        type: Boolean,
        default: false,
    },
    loading: {
        type: Boolean,
        default: false,
    },
    to: {
        type: [String, Object],
        default: null,
    },
    type: {
        type: String,
        default: "button",
    },
    outline: {
        type: Boolean,
        default: false,
    },
});
</script>
<style lang="scss">
a.app-button.light.router-link-exact-active {
    background-color: $accent-light;
    color: white;

    &:hover {
        background-color: $accent-hover !important;
        color: white !important;
    }
}
.app-button {
    min-height: 40px;
    border-radius: 10px;
    border: 1px solid $border-color;
    padding: 3px 10px;
    font-size: 16px;
    color: $text-color-secondary;
    outline: none;
    background-color: $accent-light;
    @include flex-center;
    position: relative;
    overflow: hidden;
    user-select: none;
    text-decoration: none;

    &.outline {
        background-color: transparent !important;
        border-color: $accent !important;
        color: $accent !important;
        svg {
            color: $accent !important;
        }
        &:hover {
            border-color: $accent-hover !important;
        }
    }

    &.red {
        background-color: $accent-red-light;

        &.active {
            background-color: $accent-red !important;
            color: white;
            &:hover {
                background-color: $accent-red-hover;
                color: white;
            }
        }
    }

    .button-content {
        @include flex-center;
        opacity: 1;
        transition: opacity 0.2s ease-in-out;
        transition-delay: 0.2s;

        &.loading {
            opacity: 0;
        }
    }
    .loader-container {
        position: absolute;
        inset: 0;
        isolation: isolate;
        z-index: -1;
        @include flex-center;
        transition: opacity 0.2s ease-in-out;
        opacity: 0;
        background-color: rgba(0, 0, 0, 0.02);
        transition-delay: 0.2s;
        &.active {
            opacity: 1;
            z-index: 1;
        }
        svg {
            width: 20px;
            height: 20px;
            color: white;
        }
    }
    svg {
        width: 20px;
        height: 20px;
        color: $text-color;
    }
    &.min {
        height: min-content;
        font-size: 14px;
    }

    &.active {
        color: $text-color;
        cursor: pointer;
        &.light:hover {
            background-color: $accent-light-hover;
            .loader-container svg {
                color: $text-color;
            }
        }
        &:not(.light) {
            background-color: $accent;
            color: white;
            svg {
                color: white;
            }
            &:hover {
                background-color: $accent-hover;
                color: white;
            }
        }
    }
}
</style>
