<template>
    <div class="flex align-center justify-center">
        <app-input-image
            :aspect-ratio="1"
            :image-url="imageFile"
            @file="(file) => (blobImage = file)"
            borderRadius="50%"
            size="150px"
        />
    </div>
    <app-button red @click="removeAvatarState = true" v-if="imageFile" active>
        Удалить аватар
    </app-button>
    <app-input label="Отображаемое имя" white v-model="name" />
    <app-input label="Email" white v-model="email" />
    <app-input label="Телефон" white v-model="phone" />
    <app-input label="Новый пароль" white v-model="newPassword" />
    <app-input
        label="Подтверждение пароля"
        white
        v-model="confirmPassword"
        v-if="newPassword"
    />
    <div class="flex flex-col gap-1">
        <span class="text-neutral-500 text-sm">
            Кто может видеть мероприятия на которые
            {{ userId ? "подписан пользователь" : "вы подписаны" }}:
        </span>
    </div>
    <UTabs :items="eventsTabsItems" v-model="eventsPrivate" color="neutral" />
    <app-button :active="formChangedAndValid" @click="saveChanges">
        Сохранить
    </app-button>
</template>
<script setup>
import { useAuthStore } from "~/stores/auth";
import { storeToRefs } from "pinia";
import { UsersService } from "@/client";
const authStore = useAuthStore();
const emits = defineEmits(["updateUserData"]);
const { userId } = defineProps({
    userId: {
        type: String,
        required: false,
        default: null,
    },
});

const eventsTabsItems = [
    {
        label: "Все",
        value: "all",
    },
    {
        label: "Друзья",
        value: "friends",
    },
];
const userData = ref(null);
if (userId) {
    userData.value = await UsersService.getUserFullUsersUserIdFullGet(userId);
} else {
    const { userData: localUserData } = storeToRefs(authStore);
    userData.value = localUserData.value;
}

const eventsPrivate = ref(userData.value.events_private ? "friends" : "all");
const name = ref(userData.value.name);
const email = ref(userData.value.email);
const phone = ref(userData.value.phone);
const blobImage = ref(null);
const imageFile = ref(userData.value.image);
const removeAvatarState = ref(false);
const newPassword = ref("");
const confirmPassword = ref("");

const isFormChanged = computed(() => {
    if (!userData.value) return false;
    return (
        blobImage.value !== null ||
        name.value !== userData.value.name ||
        email.value !== userData.value.email ||
        phone.value !== userData.value.phone ||
        newPassword.value !== "" ||
        confirmPassword.value !== "" ||
        eventsPrivate.value !==
            (userData.value.events_private ? "friends" : "all") ||
        imageChanged.value
    );
});

const imageChanged = computed(() => {
    return blobImage.value || removeAvatarState.value;
});

const isFormValid = computed(() => {
    return (
        name.value.trim() !== "" &&
        email.value.trim() !== "" &&
        (newPassword.value === "" ||
            newPassword.value === confirmPassword.value)
    );
});

const formChangedAndValid = computed(() => {
    return isFormChanged.value && isFormValid.value;
});

const saveChanges = async () => {
    if (!isFormChanged.value) return;
    if (!isFormValid.value) return;
    if (userId) {
        userData.value = await UsersService.updateUserUsersUserIdPut(userId, {
            ...userData.value,
            name: name.value,
            email: email.value,
            phone: phone.value,
            events_private: eventsPrivate.value === "friends",
            password: newPassword.value || null,
        });
        if (blobImage.value) {
            imageFile.value =
                await UsersService.updateUserImageUsersUserIdAvatarPut(userId, {
                    userPicture: blobImage.value,
                });
            blobImage.value = null;
        }
        if (removeAvatarState.value) {
            await UsersService.deleteUserImageUsersUserIdAvatarDelete(userId);
            removeAvatarState.value = false;
            imageFile.value = null;
        }
    } else {
        await authStore.updateProfile({
            name: name.value,
            email: email.value,
            phone: phone.value,
            events_private: eventsPrivate.value === "friends",
            password: newPassword.value || null,
        });
        if (blobImage.value) {
            imageFile.value =
                await UsersService.updateUserImageUsersMeAvatarPut({
                    userPicture: blobImage.value,
                });
            blobImage.value = null;
        }
        if (removeAvatarState.value) {
            await UsersService.deleteUserImageUsersMeAvatarDelete();
            removeAvatarState.value = false;
            imageFile.value = null;
        }
        await authStore.getUserData();
        userData.value = authStore.userData;
    }
    emits("updateUserData", userData.value);
    newPassword.value = "";
    confirmPassword.value = "";
};
</script>
<style lang="scss" scoped>
.avatar-container {
    display: flex;
    justify-content: center;
}
.avatar {
    border: 1px solid $border-color;
}
</style>
