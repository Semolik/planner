<template>
    <div :class="['file-upload', { min }, { white }]">
        <div
            class="upload-area"
            :class="[{ 'has-files': modelValue.length > 0 }, { isDragging }]"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="onDrop"
            @click="triggerFileInput"
        >
            <input
                ref="fileInput"
                type="file"
                :multiple="multiple"
                class="file-input"
                :accept="accept"
                @change="onFileChange"
            >

            <!-- Single-file mode -->
            <template v-if="!multiple">
                <div v-if="modelValue.length === 0" class="upload-placeholder">
                    <Icon
                        v-if="!min"
                        size="24px"
                        name="material-symbols:upload"
                    />
                    <p>Перетащите файл сюда или нажмите, чтобы выбрать</p>
                </div>
                <div v-else class="single-file-view">
                    <span class="file-name">
                        {{ modelValue[0].name }} ({{
                            formatSize(modelValue[0].size)
                        }})
                    </span>
                    <button
                        class="remove-btn-hover"
                        @click.stop="removeFile(0)"
                    >
                        <Icon size="16px" name="material-symbols:delete" />
                    </button>
                </div>
            </template>

            <!-- Multiple-files mode -->
            <template v-else>
                <div v-if="modelValue.length === 0" class="upload-placeholder">
                    <Icon
                        v-if="!min"
                        size="24px"
                        name="material-symbols:upload"
                    />
                    <p>
                        {{
                            !min
                                ? multiple
                                    ? "Перетащите файлы сюда или нажмите, чтобы выбрать"
                                    : "Перетащите файл сюда или нажмите, чтобы выбрать"
                                : multiple
                                  ? "Выберите файлы"
                                  : "Выберите файл"
                        }}
                    </p>
                </div>
                <div v-else class="file-list">
                    <div
                        v-for="(file, index) in modelValue"
                        :key="index"
                        class="file-item"
                        @mouseenter="hoveredIndex = index"
                        @mouseleave="hoveredIndex = null"
                        @click.stop="removeFile(index)"
                    >
                        <span
                            class="file-name"
                            :class="{ 'hovered-file': hoveredIndex === index }"
                        >
                            {{ file.name }} ({{ formatSize(file.size) }})
                        </span>
                        <button
                            v-if="hoveredIndex === index"
                            class="remove-btn-hover"
                        >
                            <Icon size="16px" name="material-symbols:delete" />
                        </button>
                    </div>
                </div>
            </template>
        </div>
    </div>
</template>

<script setup>
const props = defineProps({
    modelValue: {
        type: Array,
        default: () => [],
    },
    accept: {
        type: String,
        default: "*",
    },
    multiple: {
        type: Boolean,
        default: true,
    },
    min: {
        type: Boolean,
        default: false,
    },
    white: {
        type: Boolean,
        default: false,
    },
});

const emit = defineEmits(["update:modelValue"]);
const fileInput = ref(null);
const isDragging = ref(false);
const hoveredIndex = ref(null);

const formatSize = (size) => {
    const units = ["Б", "КБ", "МБ", "ГБ"];
    let i = 0;
    while (size >= 1024 && i < units.length - 1) {
        size /= 1024;
        i++;
    }
    return `${size.toFixed(2)} ${units[i]}`;
};

const triggerFileInput = () => {
    fileInput.value.click();
};

const onFileChange = (event) => {
    const files = Array.from(event.target.files);
    addFiles(files);
    event.target.value = null;
};

const onDrop = (event) => {
    isDragging.value = false;
    const files = Array.from(event.dataTransfer.files);
    addFiles(files);
};

const addFiles = (files) => {
    let newFiles = [];
    if (!props.multiple && files.length > 0) {
        // In single mode, keep only the first file
        newFiles = [files[0]];
    } else {
        newFiles = [...props.modelValue, ...files];
    }
    emit("update:modelValue", newFiles);
};

const removeFile = (index) => {
    const newFiles = [...props.modelValue];
    newFiles.splice(index, 1);
    emit("update:modelValue", newFiles);
};
</script>

<style lang="scss" scoped>
.file-upload {
    width: 100%;
    &.white .upload-area {
        background-color: white;
        &:hover {
            background-color: white;
        }
    }
    &.min {
        width: 100%;
        .upload-area {
            .upload-placeholder p {
                margin-top: 0;
            }
        }
    }
    .upload-area {
        position: relative;
        border: 2px dashed $accent-light;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        cursor: pointer;
        min-height: 90px;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: $secondary-bg;
        &:hover {
            border-color: black;
            background-color: $tertiary-bg;
        }

        .file-input {
            display: none;
        }
        .upload-placeholder {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: $text-color-tertiary;
            p {
                margin-top: 10px;
            }
        }
        .single-file-view {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            gap: 8px;
            .file-name {
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 250px;
            }
            .remove-btn-hover {
                background: none;
                border: none;
                cursor: pointer;
                font-size: 16px;
            }
        }
        .file-list {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            .file-item {
                position: relative;
                isolation: isolate;
                cursor: pointer;
                background-color: $quaternary-bg;
                color: $text-color-secondary;
                padding: 8px 12px;
                border-radius: 4px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 8px;
                transition:
                    background-color 0.3s ease,
                    color 0.3s ease;
                &:hover {
                    background-color: $accent-red-hover;
                    color: $primary-bg;
                    .remove-btn-hover {
                        visibility: visible;
                        opacity: 1;
                    }
                    .file-name {
                        opacity: 0;
                    }
                }
                .file-name {
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    max-width: 200px;
                    transition:
                        color 0.3s ease,
                        opacity 0.3s ease;
                    opacity: 1;
                }
                .remove-btn-hover {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    visibility: hidden;
                    opacity: 0;
                    background: none;
                    border: none;
                    color: $primary-bg;
                    cursor: pointer;
                    font-size: 20px;
                    z-index: 2;
                    transition:
                        visibility 0.3s ease,
                        opacity 0.3s ease;
                }
            }
        }
    }
}
</style>
