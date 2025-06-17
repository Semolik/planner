<template>
    <app-form
        full-height
        :headline="
            createMode
                ? 'Создание пользователя'
                : viewMode
                  ? 'Информация о пользователе'
                  : 'Редактирование пользователя'
        "
        max-width="600px"
    >
        <div :class="viewMode ? 'flex' : 'group'">
            <app-input
                v-model="username"
                label="Имя пользователя"
                required
                white
                name="username"
                :disabled="viewMode"
            />

            <app-input
                v-model="password"
                label="Пароль"
                type="password"
                required
                white
                v-if="!viewMode"
            />
        </div>
        <div class="group">
            <app-input
                v-model="firstName"
                label="Имя"
                required
                white
                :disabled="viewMode"
            />
            <app-input
                v-model="lastName"
                label="Фамилия"
                required
                white
                :disabled="viewMode"
            />
        </div>
        <div class="group">
            <app-input
                v-model="patronymic"
                label="Отчество"
                required
                white
                :disabled="viewMode"
            />
            <app-input
                v-model="birthDate"
                label="Дата рождения"
                type="date"
                white
                :disabled="viewMode"
            />
        </div>

        <div class="group">
            <app-input
                v-model="phone"
                label="Телефон"
                white
                :disabled="viewMode"
            />
            <app-input
                v-model="vk_id"
                label="VK ID"
                white
                type="number"
                :disabled="viewMode"
            />
        </div>
        <div class="grid grid-cols-2 gap-2" :class="{ viewMode }">
            <div class="flex flex-col gap-1 w-full">
                <div class="event-form-label">Институт</div>
                <USelect
                    v-model="instituteId"
                    :items="institutes"
                    white
                    value-key="id"
                    label-key="name"
                    size="lg"
                    :style="viewMode ? '' : `--ui-border-accented: transparent`"
                    :disabled="viewMode"
                />
            </div>
            <app-input
                v-model="group"
                label="Группа"
                white
                :disabled="viewMode"
            />
        </div>
        <div class="flex flex-col gap-1">
            <div class="event-form-label">Роли</div>
            <div class="flex flex-wrap gap-4 ml-2">
                <UCheckbox
                    v-for="role in roles"
                    v-model="role.selected"
                    :label="role.label"
                    color="neutral"
                    variant="card"
                    size="lg"
                    :disabled="viewMode"
                />
            </div>
        </div>
        <div class="flex flex-col gap-1" v-if="!viewMode">
            <div class="event-form-label">Тип пользователя</div>

            <UTabs color="neutral" :items="userTypes" v-model="userType" />
        </div>
        <template v-if="!viewMode">
            <app-button :active="buttonActive" @click="submit">
                {{ createMode ? "Создать" : "Сохранить" }}
            </app-button>
            <app-button
                v-if="!createMode"
                active
                red
                @click="deleteUserModalOpen = true"
            >
                Удалить
            </app-button>
        </template>
    </app-form>
    <user-delete-modal
        v-model:open="deleteUserModalOpen"
        :user="userData"
        @deleted="emit('deleted', userId)"
        v-if="!createMode"
    />
</template>
<script setup>
import { UsersService, InstitutesService, AuthService } from "@/client";
const { userId, createMode, viewMode } = defineProps({
    userId: {
        type: String,
        required: false,
        default: null,
    },
    createMode: {
        type: Boolean,
        required: false,
        default: false,
    },
    viewMode: {
        type: Boolean,
        required: false,
        default: false,
    },
});
const emit = defineEmits(["deleted", "created"]);
const institutes = await InstitutesService.getInstitutesInstitutesGet();
const username = ref("");
const deleteUserModalOpen = ref(false);
const isActive = ref(true);
const instituteId = ref("");
const firstName = ref("");
const lastName = ref("");
const patronymic = ref("");
const vk_id = ref("");
const birthDate = ref(null);
const phone = ref("");
const group = ref("");
const userData = ref(null);
const userType = ref("user");
const password = ref("");
const userTypes = [
    { label: "Пользователь", value: "user" },

    { label: "Администратор", value: "superuser" },
];
const roles = ref([
    { label: "Фотограф", value: "photographer", selected: false },

    { label: "Копирайтер", value: "copywriter", selected: false },
    { label: "Дизайнер", value: "designer", selected: false },
]);
if (userId) {
    const user = await UsersService.getUserUsersUserIdGet(userId);
    userData.value = user;
    username.value = user.username;
    userType.value = user.is_superuser ? "superuser" : "user";
    isActive.value = user.is_active;
    instituteId.value = user.institute.id;
    firstName.value = user.first_name;
    lastName.value = user.last_name;
    patronymic.value = user.patronymic;
    vk_id.value = user.vk_id || "";
    birthDate.value = user.birth_date;
    phone.value = user.phone;
    group.value = user.group;
    roles.value = roles.value.map((role) => {
        return {
            ...role,
            selected: user.roles.some((r) => r === role.value),
        };
    });
}
const selectedRoles = computed(() => {
    return roles.value
        .filter((role) => role.selected)
        .map((role) => role.value);
});
const rolesAsEquals = (a, b) => {
    if (a.length !== b.length) return false;
    return a.every((role) => b.includes(role));
};
const buttonActive = computed(
    () =>
        firstName.value.length > 0 &&
        lastName.value.length > 0 &&
        username.value.length > 0 &&
        instituteId.value.length > 0 &&
        group.value.length > 0 &&
        (createMode ||
            (userData.value &&
                (userData.value.username !== username.value ||
                    userData.value.first_name !== firstName.value ||
                    userData.value.last_name !== lastName.value ||
                    userData.value.patronymic !== patronymic.value ||
                    userData.value.institute.id !== instituteId.value ||
                    userData.value.group !== group.value ||
                    (userData.value.vk_id || "") !== vk_id.value ||
                    userData.value.birth_date !== birthDate.value ||
                    userData.value.phone !== phone.value ||
                    userData.value.is_active !== isActive.value ||
                    !rolesAsEquals(userData.value.roles, selectedRoles.value) ||
                    userType.value !==
                        (userData.value.is_superuser ? "superuser" : "user"))))
);
const { $toast } = useNuxtApp();
const submit = async () => {
    if (!buttonActive.value || viewMode) {
        return;
    }

    try {
        if (createMode) {
            const new_user = await AuthService.registerUserAuthRegisterPost({
                first_name: firstName.value,
                last_name: lastName.value,
                patronymic: patronymic.value,
                vk_id: vk_id.value,
                birth_date: birthDate.value,
                phone: phone.value,
                group: group.value,
                roles: selectedRoles.value,
                username: username.value,
                password: password.value,
                is_active: isActive.value,
                is_superuser: userType.value === "superuser",
                is_verified: true,
                institute_id: instituteId.value,
            });
            $toast.success("Пользователь успешно создан");
            emit("created", new_user);
        } else {
            userData.value = await UsersService.updateUserUsersUserIdPut(
                userId,
                {
                    username: username.value,
                    first_name: firstName.value,
                    last_name: lastName.value,
                    patronymic: patronymic.value,
                    roles: selectedRoles.value,
                    institute_id: instituteId.value,
                    group: group.value,
                    vk_id: vk_id.value || null,
                    birth_date: birthDate.value,
                    phone: phone.value,
                    is_active: isActive.value,
                    is_superuser: userType.value === "superuser",
                    password: password.value || null,
                }
            );
            vk_id.value = userData.value.vk_id ? userData.value.vk_id : "";
        }
    } catch (e) {
        console.error(e);
        $toast.error(HandleOpenApiError(e).message);
    }
};
</script>
<style scoped lang="scss">
.group {
    display: grid;
    gap: 10px;
    grid-template-columns: 1fr 1fr;

    @include md(true) {
        grid-template-columns: 1fr;
    }
}
.viewMode {
    --ui-bg: #{$tertiary-bg};
}
</style>
