<template>
    <div class="index-page">
        <div class="block" v-if="typed_tasks.length">
            <div class="head">Мои задачи</div>
            <div class="tasks">
                <div
                    class="task"
                    v-for="task in typed_tasks.slice(0, 2)"
                    :key="task.id"
                >
                    <div class="name">
                        {{ getTypedTaskName(task) }}
                    </div>
                    <div class="date">
                        {{ getTypedTaskDate(task) }}
                    </div>
                </div>
            </div>
            <app-button
                v-if="typed_tasks.length"
                :to="`/tasks/my`"
                active
                mini
                class="mt-auto"
            >
                Перейти к задачам
            </app-button>
        </div>
        <template v-for="role in sections" :key="role">
            <div class="block" v-if="notes[role] && notes[role].length">
                <div class="head">
                    {{ blockLabel[role] }}
                </div>
                <div
                    class="text"
                    v-html="
                        notes[role][0].text.replaceAll('\n', '<br>') ||
                        'Нет заметки'
                    "
                ></div>
                <div class="files" v-if="notes[role][0].files?.length">
                    <a
                        :href="file.url"
                        class="file-link"
                        target="_blank"
                        download
                        v-for="(file, idx) in notes[role][0].files"
                        :key="idx"
                    >
                        {{ file.name || file.file_name }}
                    </a>
                </div>
                <app-button
                    active
                    class="mt-auto"
                    mini
                    @click="openEditNoteModal(notes[role][0])"
                >
                    Редактировать
                </app-button>
            </div>
            <div
                class="block create"
                v-else-if="authStore.isAdmin"
                @click="
                    selectedRole = role;
                    createNoteModalOpen = true;
                "
            >
                Создать заметку для {{ labels[role] }}
            </div>
        </template>
    </div>

    <UModal
        v-model:open="createNoteModalOpen"
        v-if="selectedRole"
        :title="modalTitle"
    >
        <template #body>
            <div class="flex flex-col gap-4">
                <!-- Текст заметки -->
                <app-input
                    v-model="form.text"
                    type="textarea"
                    placeholder="Введите текст заметки"
                />

                <!-- Загрузка новых файлов -->
                <div
                    class="file-upload dashed-box"
                    @dragover.prevent
                    @drop="handleDrop"
                >
                    <input
                        type="file"
                        multiple
                        @change="handleFileUpload"
                        ref="fileInput"
                        hidden
                    />
                    <p @click="$refs.fileInput.click()">
                        Выберите файлы или перетащите их сюда
                    </p>
                </div>

                <!-- Превью новых файлов -->
                <div v-if="form.files.length" class="uploaded-files">
                    <h5>Новые файлы:</h5>
                    <ul>
                        <li v-for="(file, index) in form.files" :key="index">
                            {{ file.name }} ({{ formatBytes(file.size) }})
                            <button @click="removeFile(index)">Удалить</button>
                        </li>
                    </ul>
                </div>

                <!-- Существующие файлы -->
                <div v-if="form.currentFiles.length" class="uploaded-files">
                    <h5>Текущие файлы:</h5>
                    <ul>
                        <li
                            v-for="(file, index) in form.currentFiles"
                            :key="'current' + index"
                        >
                            {{ file.name || file.file_name }}
                            <template v-if="file.size">
                                ({{ formatBytes(file.size) }})
                            </template>
                            <app-button
                                @click="removeCurrentFile(file.id)"
                                red
                                active
                                mini
                            >
                                Удалить
                            </app-button>
                        </li>
                    </ul>
                </div>

                <!-- Кнопки -->
                <div class="flex justify-between mt-4">
                    <app-button active mini @click="submitNote">
                        Сохранить
                    </app-button>
                    <app-button
                        active
                        red
                        mini
                        @click="deleteNote"
                        v-if="isEditing"
                    >
                        Удалить
                    </app-button>
                </div>
            </div>
        </template>
    </UModal>
  <nuxt-link to="test">asdas</nuxt-link>
</template>

<script setup>
import { HomeService, UserRole, TasksService } from "~/client";
import { useAuthStore } from "~/stores/auth";

const tasks = await TasksService.getMyTasksTasksMyGet(1, "active");
// flat array of tasks
const typed_tasks = tasks.flatMap((task) => {
    return task.typed_tasks.map((t) => ({
        ...t,
        event: task.event,
        parent_task: task,
    }));
});
const authStore = useAuthStore();
const createNoteModalOpen = ref(false);
const selectedRole = ref(null);
const isEditing = ref(false);
const currentNoteId = ref(null);

// Форма
const form = reactive({
    text: "",
    files: [],
    currentFiles: [], // текущие файлы заметки
});

// Лейблы
const labels = {
    [UserRole.PHOTOGRAPHER]: "фотографов",
    [UserRole.DESIGNER]: "дизайнеров",
    [UserRole.COPYWRITER]: "копирайтеров",
};

const blockLabel = {
    [UserRole.PHOTOGRAPHER]: "Фотографам",
    [UserRole.DESIGNER]: "Дизайнерам",
    [UserRole.COPYWRITER]: "Копирайтерам",
};

const sections = [
    UserRole.PHOTOGRAPHER,
    UserRole.DESIGNER,
    UserRole.COPYWRITER,
];

// Заметки
const notes = ref({});

// Загрузка данных
async function loadNotes() {
    const notesData = await HomeService.getHomeNotesHomeNotesGet();
    notes.value = notesData.reduce((acc, note) => {
        if (!acc[note.role]) acc[note.role] = [];
        acc[note.role].push(note);
        return acc;
    }, {});
}

await loadNotes();

// Модальное окно

const modalTitle = computed(() => {
    return isEditing.value
        ? `Редактировать заметку для ${labels[selectedRole.value]}`
        : `Создать заметку для ${labels[selectedRole.value]}`;
});

function resetForm() {
    form.text = "";
    form.files = [];
    form.currentFiles = [];
    isEditing.value = false;
    currentNoteId.value = null;
}

async function openEditNoteModal(note) {
    selectedRole.value = note.role;
    form.text = note.text;
    form.currentFiles = [...note.files];
    form.files = [];
    currentNoteId.value = note.id;
    isEditing.value = true;
    createNoteModalOpen.value = true;
}

// Файлы

function handleFileUpload(event) {
    const files = Array.from(event.target.files);
    form.files.push(...files);
}

function handleDrop(event) {
    const files = Array.from(event.dataTransfer.files);
    form.files.push(...files);
}

function removeFile(index) {
    form.files.splice(index, 1);
}

async function removeCurrentFile(fileId) {
    await HomeService.deleteFileFromHomeNoteHomeNotesNoteIdFilesFileIdDelete(
        currentNoteId.value,
        fileId
    );
    form.currentFiles = form.currentFiles.filter((f) => f.id !== fileId);
}

function formatBytes(bytes) {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

// Сохранение заметки

async function submitNote() {
    let note;
    if (isEditing.value) {
        note = await HomeService.updateHomeNoteHomeNotesNoteIdPut(
            currentNoteId.value,
            {
                text: form.text,
            }
        );
    } else {
        note = await HomeService.createHomeNoteHomeNotesPost({
            role: selectedRole.value,
            text: form.text,
        });
    }

    // Загружаем новые файлы
    for (const file of form.files) {
        if (file.id) continue; // пропускаем уже загруженные

        await HomeService.addFileToHomeNoteHomeNotesNoteIdFilesPost(note.id, {
            file: file,
        });
    }

    // Обновляем список заметок
    if (!notes.value[note.role]) {
        notes.value[note.role] = [];
    }

    const existingIndex = notes.value[note.role].findIndex(
        (n) => n.id === note.id
    );

    if (existingIndex > -1) {
        notes.value[note.role].splice(existingIndex, 1); // удаляем старую
    }

    notes.value[note.role].unshift(note); // добавляем новую/обновлённую

    resetForm();
    createNoteModalOpen.value = false;
}

// Удаление заметки
async function deleteNote() {
    if (!currentNoteId.value) return;

    await HomeService.deleteHomeNoteHomeNotesNoteIdDelete(currentNoteId.value);

    // Удаляем из списка
    notes.value[selectedRole.value] = notes.value[selectedRole.value].filter(
        (note) => note.id !== currentNoteId.value
    );

    resetForm();
    createNoteModalOpen.value = false;
}
const getTypedTaskName = (task) => {
    if (task.event) {
        if (task.task_type == UserRole.PHOTOGRAPHER) {
            return `Обработка репортажа "${task.event.name}"`;
        } else if (task.task_type == UserRole.DESIGNER) {
            return `Подготовка обложки для репортажа  "${task.event.name}"`;
        } else if (task.task_type == UserRole.COPYWRITER) {
            return `Написание публикации для репортажа  "${task.event.name}"`;
        }
    }
    return task.parent_task.name + ": " + task.description;
};
const getTypedTaskDate = (task) => {
    return new Date(
        task.event ? task.event.date : task.due_date
    ).toLocaleDateString();
};
</script>

<style lang="scss" scoped>
.index-page {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));

    gap: 10px;
    @include lg {
        padding: 10px;
        gap: 20px;
    }
    .block {
        padding: 20px;
        border: 1px solid #ccc;
        border-radius: 20px;
        min-height: 80px;
        display: flex;
        gap: 10px;
        flex-direction: column;

        .tasks {
            display: flex;
            flex-direction: column;
            gap: 5px;

            .task {
                padding: 10px;
                border-bottom: 1px solid #ddd;
                border: 1px solid #ddd;
                border-radius: 10px;
                display: flex;
                flex-direction: column;
                gap: 5px;
                .name {
                    font-size: 14px;
                }

                .date {
                    font-size: 12px;
                    color: #666;
                }
            }
        }
        .head {
            font-weight: bold;
        }

        .files {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;

            .file-link {
                padding: 3px 10px;
                border: 1px solid $text-color;
                border-radius: 5px;
            }
        }

        &.create {
            align-items: center;
            justify-content: center;
            border-style: dashed;
            text-align: center;
            &:hover {
                cursor: pointer;
                border-color: $text-color;
            }
        }
    }

    .note {
        margin-bottom: 15px;
        padding: 10px;
        background: #f9f9f9;
        border-radius: 5px;
    }
}

.dashed-box {
    border: 2px dashed #ccc;
    padding: 20px;
    text-align: center;
    border-radius: 5px;
    cursor: pointer;
    transition: border-color 0.3s;

    &:hover {
        border-color: #888;
    }
}

.uploaded-files {
    ul {
        list-style-type: disc;
        padding-left: 20px;
    }

    li {
        display: flex;
        gap: 10px;
        margin-bottom: 5px;
    }

    button {
        margin-left: 10px;
        color: red;
        font-size: 0.8rem;
    }
}
</style>
