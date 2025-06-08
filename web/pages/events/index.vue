<template>
    <div class="tasks-page" ref="eventsPage">
        <app-button
            active
            v-if="authStore.isAdmin"
            color="primary"
            :to="{ name: routesNames.eventsAdd }"
        >
            Создать мероприятие
        </app-button>
        <div class="tasks">
            <task-card v-for="task in tasks" :key="task.id" :task="task" />
        </div>
    </div>
</template>

<script setup>
import { routesNames } from "@typed-router";
import { useAuthStore } from "~/stores/auth";
import { TasksService } from "~/client";
const route = useRoute();
const eventsPage = ref(null);
const isMounted = ref(false);

onMounted(() => {
    isMounted.value = true;
});

const authStore = useAuthStore();
if (!route.query.token && !authStore.logined) {
    const router = useRouter();
    router.push("/login");
}
const tasks = ref([]);
const loading = ref(false);
const page = ref(1);
const hasMore = ref(true);

const loadEvents = async () => {
    if (loading.value || !hasMore.value) return;

    loading.value = true;
    try {
        const response = await TasksService.getTasksTasksGet(
            page.value,
            false,
            false,
            null
        );
        tasks.value.push(...response);
        hasMore.value = response.length > 0;
        page.value++;
    } catch (error) {
        console.error("Failed to load tasks:", error);
    } finally {
        loading.value = false;
    }
};

loadEvents();
</script>
<style scoped lang="scss">
.tasks-page {
    display: flex;
    flex-direction: column;
    gap: 10px;

    .tasks {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
        gap: 10px;
    }
}
</style>
