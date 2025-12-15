<template>
    <div class="avatar-uploader">
        <input
            ref="fileInput"
            type="file"
            class="hidden-input"
            @change="handleFileChange"
        >
        <img v-if="imageUrl" :src="imageUrl" class="avatar" >
        <Icon v-else :name="icon" class="avatar-uploader-icon" />
        <div v-if="imageUrl" class="overlay">
            <span>Изменить</span>
        </div>
    </div>
</template>

<script setup>
const emit = defineEmits(["file"]);
const { $toast } = useNuxtApp();

const fileInput = ref(null);

const props = defineProps({
    imageUrl: {
        type: String,
        default: "",
    },
    borderRadius: {
        type: String,
        default: "50%",
    },
    aspectRatio: {
        type: [Number, String],
        default: 1,
    },
    size: {
        type: [Number, String],
        default: "100%",
    },
    icon: {
        type: String,
        default: "material-symbols:image",
    },
    maxSizeMB: {
        type: Number,
        default: 15,
    },
});
const imageUrl = ref(props.imageUrl);
const maxSizeMB = props.maxSizeMB;

const handleFileChange = (event) => {
    const rawFile = event.target.files[0];
    if (!rawFile) return;

    if (defaultBeforeUpload(rawFile)) {
        const reader = new FileReader();
        reader.onload = (e) => {
            imageUrl.value = e.target.result;
        };
        reader.readAsDataURL(rawFile);
        emit("file", rawFile);
    } else {
        imageUrl.value = "";
    }
};

const defaultBeforeUpload = (rawFile) => {
    if (rawFile.type.split("/")[0] !== "image") {
        $toast.error("Это не картинка!");
        return false;
    } else if (rawFile.size / 1024 / 1024 > maxSizeMB) {
        $toast.error("Картинка слишком большая!");
        return false;
    }
    return true;
};
</script>

<style lang="scss">
.avatar-uploader {
    position: relative;
    width: v-bind(size);
    height: v-bind(size);
    border: 2px dashed $accent-light;
    border-radius: v-bind(borderRadius);
    cursor: pointer;
    overflow: hidden;
    aspect-ratio: v-bind(aspectRatio);
    display: flex;
    justify-content: center;
    align-items: center;
    isolation: isolate;
    background-color: white;

    .hidden-input {
        opacity: 0;
        position: absolute;
        inset: 0;
        cursor: pointer;
        z-index: 1;
    }

    .overlay {
        @include flex-center;
        content: "Изменить";
        flex-direction: column;
        position: absolute;
        inset: 0;
        background-color: rgba(0, 0, 0, 0.5);
        color: #fff;
        opacity: 0;
        transition: opacity 0.3s;
        cursor: pointer;

        &:hover {
            opacity: 1;
        }
    }

    &:has(svg) {
        border-color: $text-color-tertiary;
    }

    &:hover {
        border-color: $accent;
        .overlay {
            opacity: 1;
        }
    }

    .avatar-uploader-icon {
        color: #8c939d;
        width: 40px;
        height: 40px;
        text-align: center;
    }

    .avatar {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
}
</style>
