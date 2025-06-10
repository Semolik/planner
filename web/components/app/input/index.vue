<template>
    <div
        :class="[
            'app-input',
            { white, red, 'validation-error': validationError },
        ]"
    >
        <div class="label-container" v-if="label || labelRight">
            <label class="app-input__label" v-if="label">{{ label }}</label>
            <nuxt-link
                class="app-input__label label-right"
                :to="labelRight.to"
                v-if="labelRight"
            >
                {{ labelRight.text }}
            </nuxt-link>
        </div>
        <textarea
            v-if="type === 'textarea'"
            v-model="modelValue"
            class="app-input__input"
            :placeholder="placeholder"
            v-bind="$attrs"
            rows="7"
            @blur="validateInput"
            @input="onInput"
        ></textarea>
        <input
            v-else-if="type === 'date'"
            v-model="modelValue"
            class="app-input__input"
            v-bind="$attrs"
            :placeholder="placeholder"
            :type="type"
            @change="
                (e) => {
                    onInput(e);
                    validateInput(
                        e.target.value
                            ? new Date(e.target.value).getTime()
                            : null
                    );
                }
            "
        />
        <input
            v-model="modelValue"
            class="app-input__input"
            v-bind="$attrs"
            :placeholder="placeholder"
            :type="type"
            @blur="validateInput"
            @input="onInput"
            v-else
        />
    </div>
</template>
<script setup>
const props = defineProps({
    modelValue: {
        type: [Number, String, Date],
        default: "",
    },
    white: {
        type: Boolean,
        default: false,
    },
    height: {
        type: String,
        default: "40px",
    },
    label: {
        type: String,
        default: "",
    },
    labelRight: {
        type: Object,
        default: null,
    },
    red: {
        type: Boolean,
        default: false,
    },
    type: {
        type: String,
    },
    placeholder: {
        type: String,
    },
    validator: {
        type: Function,
        default: null,
    },
    borderRadius: {
        type: String,
        default: "8px",
    },
});

const emit = defineEmits(["update:modelValue", "validationState"]);
const validationError = ref(false);
const setValidationError = (value) => {
    validationError.value = value;
};
const modelValue = computed({
    get: () => props.modelValue,
    set: (value) => emit("update:modelValue", value),
});
const validateInput = (value) => {
    if (props.validator) {
        if (props.type === "date") {
            var isValid = props.validator(
                value ? new Date(value).getTime() : null
            );
        } else {
            var isValid = props.validator(modelValue.value);
        }
        validationError.value = !isValid;
        emit("validationState", isValid);
    }
};

const onInput = (e) => {
    if (props.validator) {
        if (props.type === "date") {
            validateInput(
                e.target.value ? new Date(e.target.value).getTime() : null
            );
        } else {
            validateInput();
        }
    }
};
defineExpose({
    setValidationError,
});
</script>

<style lang="scss">
.app-input {
    display: flex;
    flex-direction: column;
    gap: 3px;
    width: 100%;

    .label-container {
        display: flex;
        align-items: center;
        .app-input__label {
            font-size: 14px;
            color: $text-color;
            text-decoration: none;
            margin-left: 3px;
            &:empty {
                display: none;
            }
        }
        a.app-input__label {
            cursor: pointer;
            &:hover {
                text-decoration: underline;
            }
        }
        .label-right {
            display: flex;
            gap: 5px;
            margin-left: auto;
        }
    }
    &.white .app-input__input {
        background-color: white;
        &:disabled {
            background-color: $tertiary-bg;
        }
    }
    &.red .app-input__input {
        border: 1px solid $accent-red;
    }
    &.validation-error .app-input__input {
        border: 1px solid $accent-red;
    }
    &__input {
        border-radius: v-bind(borderRadius);
        border: 1px solid $border-color;
        padding: 0 10px;
        font-size: 16px;
        color: $text-color;
        outline: none;
        &:focus {
            border-color: black;
        }
    }
    input {
        height: v-bind(height);
    }
    textarea {
        padding-top: 5px;
        resize: none;
    }
}
</style>
