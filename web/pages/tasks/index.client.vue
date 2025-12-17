<template>
  <div :class="['intro play-container', {'user-mode': !authStore.isAdmin}]">
    <div class="controls">
      <div class="nav-arrows">
        <UTooltip :delay-duration="0" :disabled="isSmallScreen" text="Прошлый месяц">
          <app-button active @click="prev">
            <Icon name="mdi:arrow-left"/>
          </app-button>
        </UTooltip>

        <UTooltip :delay-duration="0" :disabled="isSmallScreen" text="Следующий месяц">
          <app-button active @click="next">
            <Icon name="mdi:arrow-right"/>
          </app-button>
        </UTooltip>
      </div>

      <div class="period-label">
        {{ periodLabel }}
      </div>

      <UTooltip :delay-duration="0" :disabled="isSmallScreen"
                :text="(showTypedTasks ? 'Скрыть' : 'Показать') + ' дедлайны'">
        <app-button :outline="isSmallScreen? showTypedTasks:!showTypedTasks" active class="toggle-button"
                    @click="toggleTypedTasks">
          <Icon v-if="!isSmallScreen" class="active" name="material-symbols:calendar-clock-outline"/>
          <span v-else class="text-sm">
            {{ showTypedTasks ? 'Скрыть' : 'Показать' }} дедлайны
          </span>
        </app-button>
      </UTooltip>

      <UTooltip :delay-duration="0" :disabled="isSmallScreen" text="Только мои задачи">
        <app-button :outline="!showCurrentUserTasks" active
                    class="toggle-button" @click="showCurrentUserTasks = !showCurrentUserTasks">
          <Icon v-if="!isSmallScreen" class="active" name="mdi:account"/>
          <span v-else class="text-sm">
            Только мои задачи
          </span>
        </app-button>
      </UTooltip>

      <!-- Кнопка поиска -->
      <UTooltip :delay-duration="0" :disabled="isSmallScreen" text="Поиск">
        <app-button active @click="searchModalOpen = true">
          <Icon name="material-symbols:search"/>
        </app-button>
      </UTooltip>
    </div>

    <TuiCalendar
        v-if="!isSmallScreen"
        ref="calendarRef"
        :calendars="calendars"
        :events="filteredEvents"
        :month="options.month"
        :options="options"
        :template="popupTemplates"
        :use-detail-popup="authStore.isAdmin"
        :week="options.week"
        class="my-calendar"
        isReadOnly
        view="month"
        @beforeUpdateEvent="handleCalendarUpdate"
        @beforeDeleteEvent="handleDeleteEvent"
        @clickEvent="handleClickEvent"
    />

    <div v-else :class="['weekly-view', {empty: sortedDates.length === 0}]">
      <div v-if="sortedDates.length === 0" class="h-full flex items-center justify-center text-gray-500">
        {{
            (!showTypedTasks || showCurrentUserTasks) ? 'Нет событий по выбранным фильтрам' : 'Нет событий на этой неделе'
        }}
      </div>
      <div v-for="(dateKey, index) in sortedDates" :key="index">
        <h3>{{ formatDateHeader(dateKey) }}</h3>
        <div
            v-for="ev in filteredGroupedByDate[dateKey]"
            :key="ev.id"
            :style="{
                backgroundColor: ev.backgroundColor,
                border: `1px solid ${ev.borderColor}`,
                color: ev.color
            }"
            class="event-card"
            @click="goToEvent(ev)"
        >
          <div class="flex justify-between">
            <div class="card-title">{{ ev.title }}</div>
            <div v-if="ev.type === 'typed_task'" class="deadline-icon">
              <Icon name="material-symbols:calendar-clock-outline"/>
            </div>
          </div>

          <div v-if="ev.category === 'time'" class="card-time">
            {{ ev.start.split('T')[1].slice(0, 5) }} - {{ ev.end.split('T')[1].slice(0, 5) }}
          </div>
          <div v-if="ev.attendees" class="card-attendees">
            {{
                ev.type == 'event' ? 'Фотографы' :
                    (ev.attendees.length > 1 ? 'Исполнители' : 'Исполнитель')
            }}: <span v-html="ev.attendees.join(', ')"></span>
          </div>
          <div v-if="ev.body" class="card-body" v-html="ev.body" />...
        </div>
      </div>
    </div>

    <!-- ✅ CommandPalette ВНУТРИ Modal -->
    <UModal
        v-model:open="searchModalOpen"
        title="Поиск"
        :ui="{
            content: 'max-w-2xl h-[500px]'
        }"
    >
      <template #content>
        <UCommandPalette
            v-model:search-term="searchQuery"
            :groups="searchCommandGroups"
            :loading="isSearching"
            placeholder="Поиск по задачам, мероприятиям, группам и пользователям..."
            class="h-full"
            :ui="{
                root: 'h-full flex flex-col',
                container: 'flex-1 min-h-0 overflow-y-auto'
            }"

            :highlight-on-hover="true"
            :lazy="false"
        >
         <template #empty>
           <div class="w-full h-full flex items-center justify-center text-center px-6">
             <p class="text-sm text-gray-600">Ничего не найдено</p>
           </div>
         </template>
        </UCommandPalette>
      </template>
    </UModal>

    <!-- Модальное окно редактирования -->
    <UModal
        v-model:open="editModalOpen"
        title="Быстрое редактирование мероприятия"
        :ui="{ content: 'max-w-2xl' }"
    >
      <template #body>
        <div class="flex flex-col gap-3" v-if="editingTask">
          <app-input
              v-model="editForm.name"
              label="Название мероприятия"
              required
              white
          />
          <app-input
              v-model="editForm.date"
              type="date"
              label="Дата мероприятия"
              required
              white
          />
          <div class="flex gap-2">
            <app-input
                v-model="editForm.timeStart"
                type="time"
                label="Время начала"
                white
            />
            <app-input
                v-model="editForm.timeEnd"
                type="time"
                label="Время окончания"
                white
            />
          </div>
          <app-input
              v-model="editForm.location"
              label="Место проведения"
              required
              white
          />
          <div class="flex flex-col gap-2 mt-2">
            <app-button @click="saveEdit" :active="editFormValid && editFormChanged">
              Сохранить
            </app-button>
            <app-button @click="openFullEditPage" active>
              Открыть полную форму
            </app-button>
          </div>
        </div>
      </template>
    </UModal>

    <!-- Модальное окно удаления -->
    <UModal
        v-model:open="deleteModalOpen"
        title="Удаление мероприятия"
    >
      <template #body>
        <div class="text-md" v-if="editingTask">
          Вы действительно хотите удалить мероприятие "{{ editingTask.event?.name || editingTask.name }}"?
        </div>
        <div class="grid grid-cols-2 gap-2 mt-4">
          <app-button active red @click="confirmDelete">
            Удалить
          </app-button>
          <app-button @click="deleteModalOpen = false">
            Отмена
          </app-button>
        </div>
      </template>
    </UModal>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'no-padding'
});

import {useRouter, useRoute} from 'vue-router';
import {watch, onMounted, onBeforeUnmount, ref, computed, nextTick} from 'vue';
import TuiCalendar from 'toast-ui-calendar-vue3';
import 'toast-ui-calendar-vue3/styles.css';
import {CalendarService, TasksService, EventsService, SearchService} from '@/client';
import { useAuthStore } from '~/stores/auth';
import { useLocalStorage } from '@vueuse/core';
import { routesNames } from '@typed-router';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const isSmallScreen = ref(false);
const calendarRef = ref();
const currentDate = ref(new Date());

const myEvents = ref([]);
const showTypedTasks = useLocalStorage('showTypedTasks', false);
const showCurrentUserTasks = useLocalStorage('showCurrentUserTasks', false);

// Сохраняем текущее событие для кнопки "Открыть"
const currentPopupEvent = ref(null);

const userTypesMap = {
    photographer: 'Фотографов',
    copywriter: 'Копирайтеров',
    designer: 'Дизайнеров',
};

const userTypesMap2 = {
    photographer: 'Фотографы',
    copywriter: 'Копирайтеры',
    designer: 'Дизайнеры',
};

const calendars = ref([
    {
        id: 'user',
        name: 'Дни рождения',
        backgroundColor: '#ff69b461',
        borderColor: '#ff69b461',
        dragBackgroundColor: '#ff69b461',
    },
    {
        id: 'task',
        name: 'Задачи',
        backgroundColor: '#2d9fff61',
        borderColor: '#2d9fff61',
        dragBackgroundColor: '#2d9fff61',
    },
    {
        id: 'photographer',
        name: 'Фотограф',
        backgroundColor: '#69ff7061',
        borderColor: '#69ff7061',
        dragBackgroundColor: '#69ff7061',
    },
    {
        id: 'copywriter',
        name: 'Копирайтер',
        backgroundColor: '#ffff0061',
        borderColor: '#ffff0061',
        dragBackgroundColor: '#ffff0061',
    },
    {
        id: 'designer',
        name: 'Дизайнер',
        backgroundColor: '#ff00ff61',
        borderColor: '#ff00ff61',
        dragBackgroundColor: '#ff00ff61',
    },
    {
        id: 'event',
        name: 'События',
        backgroundColor: '#6cc24a61',
        borderColor: '#52923561',
        dragBackgroundColor: '#6cc24a61',
    },
]);

const colors = {
    inProgress: {
        backgroundColor: '#66b3ff',
        borderColor: '#3399ff',
        color: '#ffffff',
    },
    overdueOrNoAssignees: {
        backgroundColor: '#ff4d4d',
        borderColor: '#cc0000',
        color: '#ffffff',
    },
    noPhotographersAndPassedOrComplited: {
        backgroundColor: '#d3d3d3',
        borderColor: '#6e6e6e',
        color: '#3b3b3b',
    },
};

// Опции календаря
const options = ref({
    month: { startDayOfWeek: 1 },
    week: { startDayOfWeek: 1 },
});

// Шаблоны для popup'а календаря
const popupTemplates = ref({
    popupDetailLocation: () => '',
    popupDetailUser: () => '',
    popupDetailAttendees: () => '',
    popupEdit: () => 'Редактировать',
    popupDelete: () => 'Удалить',
});

// Формат даты YYYY-MM-DD
const formatDate = (d: Date) => {
  return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2,'0')}-${d.getDate().toString().padStart(2,'0')}`;
}

// Формат месяца YYYY-MM
const formatMonth = (d: Date) => {
  return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2,'0')}`;
}

// Получение начала и конца недели по дате (понедельник - воскресенье)
const getWeekStartEnd = (date: Date) => {
  const day = date.getDay();
  const diff = (day === 0 ? 6 : day - 1);
  const start = new Date(date);
  start.setHours(0,0,0,0);
  start.setDate(start.getDate() - diff);
  const end = new Date(start);
  end.setDate(end.getDate() + 6);
  end.setHours(23,59,59,999);
  return {start, end};
}

// Обновление URL параметра period
function updateUrl() {
  const now = new Date();
  if (isSmallScreen.value) {
    const {start} = getWeekStartEnd(currentDate.value);
    const startStr = formatDate(start);
    const {start: currentWeekStart} = getWeekStartEnd(now);
    const currentWeekStartStr = formatDate(currentWeekStart);
    if (startStr === currentWeekStartStr) {
      router.replace({query: {...route.query, period: undefined}});
    } else {
      router.replace({query: {...route.query, period: startStr}});
    }
  } else {
    const monthStr = formatMonth(currentDate.value);
    const currentMonthStr = formatMonth(now);
    if (monthStr === currentMonthStr) {
      router.replace({query: {...route.query, period: undefined}});
    } else {
      router.replace({query: {...route.query, period: monthStr}});
    }
  }
}

// Установка currentDate из параметра period в URL
function setDateFromUrl() {
  const periodParam = route.query.period;
  if (periodParam && typeof periodParam === 'string') {
    if (isSmallScreen.value) {
      const d = new Date(periodParam);
      if (!isNaN(d.getTime())) {
        currentDate.value = d;
      }
    } else {
      const parts = periodParam.split('-');
      if (parts.length === 2) {
        const y = parseInt(parts[0]);
        const m = parseInt(parts[1]) - 1;
        if (!isNaN(y) && !isNaN(m)) {
          currentDate.value = new Date(y, m, 1);
        }
      }
    }
  } else {
    currentDate.value = new Date();
  }
}

// Период для отображения в шапке
const periodLabel = computed(() => {
    const date = currentDate.value;
    if (!isSmallScreen.value) {
        const monthName = date.toLocaleString('ru-RU', {month: 'long'});
        const year = date.getFullYear();
        return `${monthName.charAt(0).toUpperCase() + monthName.slice(1)} ${year}`;
    } else {
        const day = date.getDay();
        const diff = (day === 0 ? 6 : day - 1);
        const start = new Date(date);
        start.setDate(start.getDate() - diff);
        const end = new Date(start);
        end.setDate(end.getDate() + 6);
        const startDay = start.getDate();
        const endDay = end.getDate();
        const monthStart = start.toLocaleString('ru-RU', {month: 'long'});
        const monthEnd = end.toLocaleString('ru-RU', {month: 'long'});
        const year = end.getFullYear();
        if (monthStart === monthEnd) {
            return `${startDay} – ${endDay} ${monthEnd.charAt(0).toUpperCase() + monthEnd.slice(1)} ${year}`;
        } else {
            return `${startDay} ${monthStart.charAt(0).toUpperCase() + monthStart.slice(1)} – ${endDay} ${monthEnd.charAt(0).toUpperCase() + monthEnd.slice(1)} ${year}`;
        }
    }
});

// Фильтрация событий для отображения
const filteredEvents = computed(() => {
    let events = myEvents.value;
    if (!showTypedTasks.value) {
        events = events.filter(ev => ev.calendarId !== 'photographer' && ev.calendarId !== 'copywriter' && ev.calendarId !== 'designer');
    }
    if (showCurrentUserTasks.value) {
        const currentUserId = authStore.userData?.id ?? null;
        if (!currentUserId) return [];
        events = events.filter(ev => {
            if (ev.users && ev.users.length) {
                return ev.users.some(u => u?.id === currentUserId);
            }
            return false;
        });
    }
    return events;
});

// Группировка событий по дате
const filteredGroupedByDate = computed(() => {
    const groups: any = {};
    filteredEvents.value.forEach((ev) => {
        const dateKey = ev.start.split('T')[0];
        if (!groups[dateKey]) groups[dateKey] = [];
        groups[dateKey].push(ev);
    });
    return groups;
});

const sortedDates = computed(() => Object.keys(filteredGroupedByDate.value).sort());

const formatDateHeader = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleString('ru-RU', {weekday: 'long', day: 'numeric', month: 'long'});
};

// Получение периода для запроса данных
const getFetchPeriod = () => {
  if (!isSmallScreen.value && calendarRef.value) {
    const instance = calendarRef.value.getInstance();
    return {
      from: formatDate(instance.getDateRangeStart().toDate()),
      to: formatDate(instance.getDateRangeEnd().toDate())
    };
  } else {
    const {start, end} = getWeekStartEnd(currentDate.value);
    return {
      from: formatDate(start),
      to: formatDate(end)
    };
  }
}

// Загрузка событий с сервера
const fetchEvents = async () => {
    const {from: dateFrom, to: dateTo} = getFetchPeriod();

    try {
        const response = await CalendarService.getCalendarCalendarGet(dateFrom, dateTo);

        const allItems: any[] = [];
        for (const date in response) {
            response[date].forEach((calendarItem: any) => {
                allItems.push({date, item: calendarItem.item, type: calendarItem.item_type});
            });
        }

        const users = allItems.filter(i => i.type === 'user');
        const tasksWithEvents = allItems.filter(i => i.type === 'task' && i.item.event);
        const simpleTasks = allItems.filter(i => i.type === 'task' && !i.item.event);
        const typedTasks = allItems.filter(i => i.type === 'typed_task');
        const events = allItems.filter(i => i.type === 'event');

        tasksWithEvents.sort((a: any, b: any) => {
            const timeA = a.item.event.start_time;
            const timeB = b.item.event.start_time;
            return timeA.localeCompare(timeB);
        });

        const sortedItems = [...users, ...events, ...tasksWithEvents, ...simpleTasks, ...typedTasks];

        const newEvents = sortedItems.map((entry: any) => {
            const {date, item, type} = entry;
            let event: any = {
                id: `${type}-${item.id}`,
                title: '',
                start: '',
                end: '',
                category: 'task',
                isReadonly: true,
                calendarId: type,
                state: null,
                attendees: null,
                users: [],
                type: type,
            };

            if (type === 'user') {
                event.title = `День рождения: ${item.first_name} ${item.last_name}`;
                event.start = `${date}T00:00:00`;
                event.end = `${date}T23:59:59`;
                event.category = 'allday';
            } else if (type === 'task') {
                event.title = item.displayed_name;
                event.start = `${date}T00:00:00`;
                event.end = `${date}T23:59:59`;
                event.category = 'allday';
                let users = [];
                for (const typedTask of item.typed_tasks) {
                    if (typedTask.task_states.length > 0) {
                        typedTask.task_states.forEach((state: any) => {
                            users.push(state.user);
                        });
                    }
                }
                event.attendees = users.length > 0 ? users.map((user: any) => user.first_name + " " + user.last_name) : null;
                event.users = users;
            } else if (type === 'typed_task') {
                event.attendees = item.task_states.length > 0 ? item.task_states.map((state: any) => state.user.first_name + " " + state.user.last_name) : null;
                event.users = item.task_states.length > 0 ? item.task_states.map((state: any) => state.user) : [];
                event.id = `task-${item.parent_task.id}`;
                event.category = 'allday';
                event.start = `${item.due_date}T00:00:00`;
                event.end = `${item.due_date}T23:59:59`;
                event.calendarId = item.task_type;
                let eventName = item.parent_task.displayed_name;
                if (item.parent_task.event) {
                    eventName = item.parent_task.event.name;
                    if (item.task_type === 'photographer') {
                        event.title = `Сдача репортажа "${eventName}"`;
                    } else if (item.task_type === 'copywriter') {
                        event.title = `Текст публикации к мероприятию "${eventName}"`;
                    } else if (item.task_type === 'designer') {
                        event.title = `Обложка на альбом "${eventName}"`;
                    }
                } else {
                    event.title = eventName;
                }

                const inProgress = item.task_states.some((state: any) => state.state === 'pending');
                if (item.parent_task.event) {
                    const isPassed = item.parent_task.event.is_passed;
                    const hasAssignedPhotographers = item.parent_task.event.has_assigned_photographers;
                    const allCompleted = item.parent_task.all_typed_tasks_completed;
                    if (!hasAssignedPhotographers && isPassed) {
                        event.backgroundColor = colors.noPhotographersAndPassedOrComplited.backgroundColor;
                        event.borderColor = colors.noPhotographersAndPassedOrComplited.borderColor;
                        event.color = colors.noPhotographersAndPassedOrComplited.color;
                    } else if (hasAssignedPhotographers) {
                        if (allCompleted) {
                            event.backgroundColor = colors.noPhotographersAndPassedOrComplited.backgroundColor;
                            event.borderColor = colors.noPhotographersAndPassedOrComplited.borderColor;
                            event.color = colors.noPhotographersAndPassedOrComplited.color;
                        } else if (inProgress) {
                            if (item.due_date_passed) {
                                event.backgroundColor = colors.overdueOrNoAssignees.backgroundColor;
                                event.borderColor = colors.overdueOrNoAssignees.borderColor;
                                event.color = colors.overdueOrNoAssignees.color;
                                event.title = '! ' + event.title;
                            } else {
                                event.backgroundColor = colors.inProgress.backgroundColor;
                                event.borderColor = colors.inProgress.borderColor;
                                event.color = colors.inProgress.color;
                            }
                        }
                    } else {
                        event.backgroundColor = colors.overdueOrNoAssignees.backgroundColor;
                        event.borderColor = colors.overdueOrNoAssignees.borderColor;
                        event.color = colors.overdueOrNoAssignees.color;
                    }
                } else {
                    if (item.due_date_passed) {
                        event.backgroundColor = colors.overdueOrNoAssignees.backgroundColor;
                        event.borderColor = colors.overdueOrNoAssignees.borderColor;
                        event.color = colors.overdueOrNoAssignees.color;
                        event.title = '! ' + event.title;
                    } else if (inProgress) {
                        event.backgroundColor = colors.inProgress.backgroundColor;
                        event.borderColor = colors.inProgress.borderColor;
                        event.color = colors.inProgress.color;
                    } else {
                        event.backgroundColor = colors.noPhotographersAndPassedOrComplited.backgroundColor;
                        event.borderColor = colors.noPhotographersAndPassedOrComplited.borderColor;
                        event.color = colors.noPhotographersAndPassedOrComplited.color;
                    }
                }
                event.body = item.description;
            } else if (type === 'event') {
                event.id = `task-${item.task.id}`;
                event.title = item.name;
                event.start = `${item.date}T${item.start_time}`;
                event.end = `${item.date}T${item.end_time}`;
                event.category = 'allday';

                let info_message = '';
                const isPassed = item.is_passed ?? false;

                const photographers: any[] = [];
                let assignedPhotographersCount = 0;
                if (item.task && item.task.typed_tasks) {
                    const statusMap: any = {photographer: 'green', copywriter: 'green', designer: 'green'};
                    let users: any[] = [];
                    item.task.typed_tasks.forEach((typedTask: any) => {
                        if (typedTask.task_states.length > 0) {
                            typedTask.task_states.forEach((state: any) => {
                                users.push(state.user);
                            });
                        }
                        const has_pendingState = typedTask.task_states.some((state: any) => state.state === 'pending');
                        const all_completed = typedTask.task_states.filter((state: any) => state.state === 'completed').length > 0 &&
                            typedTask.task_states.every((typed_task: any) => typed_task.state === 'completed' || typed_task.state === 'canceled');
                        let spanColor = isSmallScreen.value ? 'black' : 'red';
                        if (typedTask.due_date_passed && has_pendingState) {
                            statusMap[typedTask.task_type] = 'red';
                            info_message += `<span style="color: ${spanColor}"> Просрочен срок сдачи ${userTypesMap[typedTask.task_type]}. </span>`+(isSmallScreen.value?'':'<br>');
                        } else if (has_pendingState) {
                            if (statusMap[typedTask.task_type] !== 'red') {
                                statusMap[typedTask.task_type] = 'yellow';
                            }
                        } else if (!all_completed && item.has_assigned_photographers) {
                            statusMap[typedTask.task_type] = 'red';
                            info_message += `<span style="color: ${spanColor}"> Не выполнена задача ${userTypesMap[typedTask.task_type]}. </span>`+(isSmallScreen.value?'':'<br>');
                        }
                        if (typedTask.task_type === 'photographer' && typedTask.task_states) {
                            const activeStates = typedTask.task_states.filter((state: any) => state.state !== 'canceled');
                            assignedPhotographersCount += activeStates.length;
                            typedTask.task_states.forEach((state: any) => {
                                let name = state.user.first_name + " " + state.user.last_name;
                                photographers.push(state.state === 'canceled' ? `<span style="color: ${spanColor}">${name}</span>` : name);
                            });
                        }
                    });
                    event.users = users;
                    const colorMap = {red: '#e94e4e', yellow: '#ffd54f', green: '#6cc24a'};

                    if (assignedPhotographersCount > 0) {
                        let circles = '<div style="display:flex;gap:5px;flex-wrap: wrap;">';
                        ['photographer', 'copywriter', 'designer'].forEach((type) => {
                            const color = colorMap[statusMap[type]];
                            const label = userTypesMap2[type] || type;
                            circles += `<span style="display:inline-flex; padding: 1px 8px;border-radius: 10px;border: 1px solid black;align-items:center;gap:6px;${isSmallScreen.value?'background-color: black;color: white;':''}">${label}<span style="width:12px;height:12px;border-radius:50%;background:${color};display:inline-block"></span></span>`;
                        });
                        circles += '</div>';
                        info_message += circles;
                    }
                }
                if (info_message.length > 0) {
                    event.body = info_message;
                }
                event.attendees = photographers.length > 0 ? photographers : null;

                if (isPassed) {
                    const typedTasks = item.task?.typed_tasks || [];
                    const inProgress = typedTasks.some((tt: any) => tt.task_states.some((s: any) => s.state === 'pending'));
                    const isPastAnyDeadline = typedTasks.some((tt: any) => tt.due_date_passed && (tt.task_states.some((s: any) => s.state === 'pending') || tt.task_states.length == 0));

                    if (!item.has_assigned_photographers) {
                        event.backgroundColor = '#d3d3d3';
                        event.borderColor = '#6e6e6e';
                        event.color = '#3b3b3b';
                    } else if (item.task.all_typed_tasks_completed) {
                        event.backgroundColor = '#d3d3d3';
                        event.borderColor = '#6e6e6e';
                        event.color = '#3b3b3b';
                    } else if (inProgress && !isPastAnyDeadline) {
                        event.backgroundColor = '#ffd54f';
                        event.borderColor = '#cca800';
                        event.color = '#000000';
                    } else if (isPastAnyDeadline) {
                        event.backgroundColor = '#e94e4e';
                        event.borderColor = '#b53232';
                        event.color = isSmallScreen.value? 'black': 'white';
                        event.title = '! ' + event.title;
                    }
                } else {
                    event.backgroundColor = '#6cc24a';
                    event.borderColor = '#529235';
                    event.color = '#000000';
                }
            }
            return event;
        });

        myEvents.value = newEvents;
    } catch (error) {
        console.error('Ошибка при получении данных календаря:', error);
    }
};

const next = () => {
    if (!isSmallScreen.value && calendarRef.value) {
        const instance = calendarRef.value.getInstance();
        instance.next();
        currentDate.value = instance.getDate().toDate();
    } else {
        const newDate = new Date(currentDate.value);
        newDate.setDate(newDate.getDate() + 7);
        currentDate.value = newDate;
    }
    fetchEvents();
};

const prev = () => {
    if (!isSmallScreen.value && calendarRef.value) {
        const instance = calendarRef.value.getInstance();
        instance.prev();
        currentDate.value = instance.getDate().toDate();
    } else {
        const newDate = new Date(currentDate.value);
        newDate.setDate(newDate.getDate() - 7);
        currentDate.value = newDate;
    }
    fetchEvents();
};

const toggleTypedTasks = () => {
    showTypedTasks.value = !showTypedTasks.value;
};

// Инициализация кнопки "Открыть" в popup'е
const setupPopupOpenButton = () => {
    let mutationObserver: MutationObserver | null = null;

    const setupButton = () => {
        const popup = document.querySelector('.toastui-calendar-popup-container');
        if (!popup || popup.querySelector('.popup-open-btn')) return;

        const buttonContainer = popup.querySelector('.toastui-calendar-section-button');
        if (!buttonContainer) return;

        const openBtn = document.createElement('button');
        openBtn.className = 'popup-open-btn';
        openBtn.textContent = 'Открыть';
        openBtn.style.width = '100%';
        openBtn.style.textAlign = 'center';
        openBtn.style.display = 'flex';
        openBtn.style.alignItems = 'center';
        openBtn.style.justifyContent = 'center';
        openBtn.style.padding = '12px';
        openBtn.style.borderTop = '1px solid #e5e5e5';
        openBtn.style.borderRadius = '0 0 8px 8px';

        openBtn.style.cursor = 'pointer';
        openBtn.style.fontSize = '12px';
        openBtn.style.fontWeight = '500';
        openBtn.style.transition = 'background-color 0.2s';
        openBtn.style.border = 'none';

        openBtn.addEventListener('click', (e) => {
            if (currentPopupEvent.value) {
                goToEvent(currentPopupEvent.value);
            }
        });

        buttonContainer.appendChild(openBtn);
    };

    mutationObserver = new MutationObserver(setupButton);
    mutationObserver.observe(document.body, { childList: true, subtree: true });

    return () => mutationObserver?.disconnect();
};

// Модальные окна
const editModalOpen = ref(false);
const deleteModalOpen = ref(false);
const editingTask = ref(null);
const editForm = ref({
    name: '',
    date: '',
    timeStart: '',
    timeEnd: '',
    location: '',
});

// ✅ Переменные для поиска
const searchModalOpen = ref(false);
const searchQuery = ref("");
const searchResults = ref([]);
const isSearching = ref(false);

// ✅ Вычисляемое свойство для групп
const searchCommandGroups = computed(() => {
    if (!searchResults.value.length) {
        return [];
    }

    const groups = [];
    const taskResults = searchResults.value.filter((r) => r.type === 'task');
    const eventResults = searchResults.value.filter((r) => r.type === 'event');
    const groupResults = searchResults.value.filter((r) => r.type === 'group');
    const userResults = searchResults.value.filter((r) => r.type === 'user');

    // Сначала показываем мероприятия
    if (eventResults.length > 0) {
        groups.push({
            id: 'events',
            key: 'events',
            label: 'Мероприятия',
            items: eventResults.map((r) => ({
                id: `event-${r.data.id}`,
                label: `${r.data.name} (${r.data.date})`,
                suffix: r.data.location,
                icon: 'i-heroicons-calendar',
                to: { name: routesNames.tasksTaskId, params: { task_id: r.data.task_id } }
            })),
            ignoreFilter: true
        });
    }

    // Потом задачи
    if (taskResults.length > 0) {
        groups.push({
            id: 'tasks',
            key: 'tasks',
            label: 'Задачи',
            items: taskResults.map((r) => ({
                id: `task-${r.data.id}`,
                label: r.data.name,
                icon: 'i-heroicons-document-text',
                to: { name: routesNames.tasksTaskId, params: { task_id: r.data.id } }
            })),
            ignoreFilter: true
        });
    }

    if (groupResults.length > 0) {
        groups.push({
            id: 'groups',
            key: 'groups',
            label: 'Группы мероприятий',
            items: groupResults.map((r) => ({
                id: `group-${r.data.id}`,
                label: r.data.name,
                suffix: `${r.data.events_count} мероприятий`,
                icon: 'i-heroicons-folder',
                to: { name: routesNames.eventsGroupsGroupId, params: { group_id: r.data.id } }
            })),
            ignoreFilter: true
        });
    }

    if (userResults.length > 0) {
        groups.push({
            id: 'users',
            key: 'users',
            label: 'Пользователи',
            items: userResults.map((r) => ({
                id: `user-${r.data.id}`,
                label: `${r.data.first_name} ${r.data.last_name}`,
                suffix: r.data.group,
                icon: 'i-heroicons-user',
                to: { name: routesNames.usersUserId, params: { user_id: r.data.id } }
            })),
            ignoreFilter: true
        });
    }

    return groups;
});

const editFormValid = computed(() => {
    return editForm.value.name.length > 0 &&
           editForm.value.date.length > 0 &&
           editForm.value.location.length > 0;
});

// Флаг изменения формы относительно исходных данных задачи
const editFormChanged = computed(() => {
    if (!editingTask.value) return false;
    const ev = editingTask.value.event;
    if (!ev) return false;
    const origName = ev.name || '';
    const origDate = ev.date || '';
    const origStart = ev.start_time ? ev.start_time.slice(0,5) : '';
    const origEnd = ev.end_time ? ev.end_time.slice(0,5) : '';
    const origLoc = ev.location || '';

    return (
        editForm.value.name !== origName ||
        editForm.value.date !== origDate ||
        editForm.value.timeStart !== origStart ||
        editForm.value.timeEnd !== origEnd ||
        editForm.value.location !== origLoc
    );
});

const openEditModal = async (taskId: string | number) => {
    try {
        const task = await TasksService.getTaskByIdTasksTaskIdGet(taskId);
        editingTask.value = task;
        if (task.event) {
            editForm.value = {
                name: task.event.name,
                date: task.event.date,
                timeStart: task.event.start_time ? task.event.start_time.slice(0, 5) : '',
                timeEnd: task.event.end_time ? task.event.end_time.slice(0, 5) : '',
                location: task.event.location,
            };
        }
        editModalOpen.value = true;
    } catch (error) {
        console.error('Ошибка загрузки задачи:', error);
    }
};

const openDeleteModal = async (taskId: string | number) => {
    try {
        const task = await TasksService.getTaskByIdTasksTaskIdGet(taskId);
        editingTask.value = task;
        deleteModalOpen.value = true;
    } catch (error) {
        console.error('Ошибка загрузки задачи:', error);
    }
};

const saveEdit = async () => {
    if (!editingTask.value || !editFormValid.value) return;

    try {
        if (editingTask.value.event) {
            await EventsService.updateEventEventsEventIdPut(editingTask.value.event.id, {
                ...editingTask.value.event,
                name: editForm.value.name,
                date: editForm.value.date,
                start_time: editForm.value.timeStart ? `${editForm.value.timeStart}:00` : null,
                end_time: editForm.value.timeEnd ? `${editForm.value.timeEnd}:00` : null,
                location: editForm.value.location,
            });
        }
        editModalOpen.value = false;
        fetchEvents();
    } catch (error) {
        console.error('Ошибка сохранения:', error);
    }
};

const confirmDelete = async () => {
    if (!editingTask.value) return;

    try {
        await TasksService.deleteTaskTasksTaskIdDelete(editingTask.value.id);
        deleteModalOpen.value = false;
        fetchEvents();
    } catch (error) {
        console.error('Ошибка удаления:', error);
    }
};

const openFullEditPage = () => {
    if (editingTask.value) {
        editModalOpen.value = false;
        router.push({
            name: routesNames.tasksTaskIdEdit.index,
            params: { task_id: editingTask.value.id }
        });
    }
};

// ✅ Обработчики событий календаря
function handleCalendarUpdate(payload) {
    if (!payload?.event) return false;

    const eventId = payload.event.id;
    if (eventId?.startsWith('task-')) {
        const taskId = eventId.replace('task-', '');
        openEditModal(taskId);
    }

    return false;
}

const handleDeleteEvent = (payload) => {
    if (!payload?.event) return false;

    const eventId = payload.event.id;
    if (eventId?.startsWith('task-')) {
        const taskId = eventId.replace('task-', '');
        openDeleteModal(taskId);
    }

    return false;
};

const performSearch = async () => {
    if (!searchQuery.value) {
        searchResults.value = [];
        return;
    }

    isSearching.value = true;
    try {
        const response = await SearchService.searchSearchGet(searchQuery.value, 50);
        searchResults.value = response.results;
    } catch (error) {
        console.error('Ошибка поиска:', error);
        searchResults.value = [];
    } finally {
        isSearching.value = false;
    }
};

// Функция загрузки ближайших мероприятий
const loadUpcomingEvents = async () => {
    isSearching.value = true;
    try {
        // Берем период: неделя вперёд от текущей даты
        const now = new Date();
        const weekLater = new Date(now);
        weekLater.setDate(now.getDate() + 7);

        const formatDateLocal = (d: Date) => {
            return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`;
        };

        const dateFrom = formatDateLocal(now);
        const dateTo = formatDateLocal(weekLater);

        const response = await CalendarService.getCalendarCalendarGet(dateFrom, dateTo);

        // Преобразуем события календаря в формат для поиска
        const results: any[] = [];
        const addedTaskIds = new Set<string>();
        const addedEventIds = new Set<string>();

        if (response && typeof response === 'object') {
            Object.entries(response).forEach(([dateKey, dayItems]: [string, any]) => {
                if (Array.isArray(dayItems)) {
                    dayItems.forEach((dayItem: any) => {
                        const itemType = dayItem.item_type;
                        const item = dayItem.item;

                        if (!item) return;

                        // Обрабатываем события
                        if (itemType === 'event' && !addedEventIds.has(item.id)) {
                            results.push({
                                type: 'event',
                                data: {
                                    id: item.id,
                                    name: item.name,
                                    date: item.date,
                                    location: item.location,
                                    task_id: item.task?.id
                                }
                            });
                            addedEventIds.add(item.id);
                        }

                        // Обрабатываем typed_task (подзадачи)
                        if (itemType === 'typed_task' && item.parent_task) {
                            const parentTask = item.parent_task;

                            // Если есть событие у родительской задачи, добавляем его
                            if (parentTask.event && !addedEventIds.has(parentTask.event.id)) {
                                results.push({
                                    type: 'event',
                                    data: {
                                        id: parentTask.event.id,
                                        name: parentTask.event.name,
                                        date: parentTask.event.date,
                                        location: parentTask.event.location,
                                        task_id: parentTask.id
                                    }
                                });
                                addedEventIds.add(parentTask.event.id);
                            }
                        }
                    });
                }
            });
        }

        searchResults.value = results;
    } catch (error) {
        console.error('Ошибка загрузки ближайших мероприятий:', error);
        searchResults.value = [];
    } finally {
        isSearching.value = false;
    }
};

let searchTimeout: NodeJS.Timeout | null = null;
watch(searchQuery, async (newQuery) => {
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }

    if (newQuery) {
        searchTimeout = setTimeout(async () => {
            await performSearch();
        }, 300);
    } else {
        // При очистке поля поиска загружаем ближайшие мероприятия
        await loadUpcomingEvents();
    }
});

// ✅ Следим за открытием/закрытием модалки
watch(searchModalOpen, async (isOpen) => {
    if (isOpen) {
        // При открытии загружаем ближайшие мероприятия
        if (!searchQuery.value) {
            await loadUpcomingEvents();
        }
    } else {
        // При закрытии очищаем
        searchQuery.value = '';
        searchResults.value = [];
    }
});

const goToSearchResult = (result) => {
    searchModalOpen.value = false;
    searchQuery.value = '';
    searchResults.value = [];

    switch (result.type) {
        case 'task':
            router.push({
                name: routesNames.tasksTaskId,
                params: { task_id: result.data.id }
            });
            break;
        case 'event':
            router.push({
                name: routesNames.tasksTaskId,
                params: { task_id: result.data.task_id }
            });
            break;
        case 'group':
            router.push({
                name: routesNames.eventsGroupsGroupId,
                params: { group_id: result.data.id }
            });
            break;
        case 'user':
            router.push({
                name: routesNames.usersUserId,
                params: { user_id: result.data.id }
            });
            break;
    }
};

function goToEvent(ev) {
    if (ev.id.startsWith('task-')) {
        const parts = ev.id.split('-');
        const typedTaskId = parts.slice(1).join('-');
        router.push({name: routesNames.tasksTaskId, params: {task_id: typedTaskId}});
    } else if (ev.calendarId === 'photographer' || ev.title.startsWith('Сдача репортажа')) {
        const typedTaskId = ev.id.split('-').slice(1).join('-');
        router.push({name: routesNames.tasksTaskId, params: {task_id: typedTaskId}});
    }
}

const handleClickEvent = (ev) => {
    currentPopupEvent.value = ev.event;

    if (!authStore.isAdmin) {
        goToEvent(ev.event);
    }
};

onMounted(async () => {
    isSmallScreen.value = window.innerWidth < 768;

    // Устанавливаем текущую дату по умолчанию (ближайшие мероприятия)
    currentDate.value = new Date();
    setDateFromUrl();

    await nextTick();
    if (!isSmallScreen.value && calendarRef.value) {
        calendarRef.value.getInstance().setDate(currentDate.value);
    }

    // Инициализация popup'а
    const cleanupPopup = setupPopupOpenButton();

    // Загрузка событий
    await fetchEvents();

    // Обновление URL при изменении даты
    watch(() => currentDate.value, updateUrl);

    // Переподгрузка событий при изменении фильтров
    watch([showTypedTasks, showCurrentUserTasks], fetchEvents);

    onBeforeUnmount(() => {
        cleanupPopup();
    });
});

onBeforeUnmount(() => {
    // cleanup if needed
});
</script>

<style scoped>
.intro {
    display: flex;
    flex-direction: column;
    gap: 20px;
    width: 100%;
    height: 100%;
}

.controls {
    display: flex;
    gap: 8px;
    align-items: center;
    flex-wrap: wrap;
    padding: 10px;
}

.nav-arrows {
    display: flex;
    gap: 8px;
    align-items: center;
}

.period-label {
    font-size: 18px;
    font-weight: 600;
    color: var(--color-text);
    flex: 1;
    margin-left: 20px;
}

.toggle-button {
    white-space: nowrap;
}

.my-calendar {
    flex: 1;
    overflow: auto;
    width: 100%;
}

.weekly-view {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding: 20px;
    overflow-y: auto;
    width: 100%;
}

.weekly-view.empty {
    justify-content: center;
    align-items: center;
}

.weekly-view h3 {
    font-size: 16px;
    font-weight: 600;
    margin: 0;
    padding: 10px 0;
    border-bottom: 2px solid var(--color-border);
    text-transform: capitalize;
}

.event-card {
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.event-card:hover {
    transform: translateX(2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-title {
    font-weight: 500;
    font-size: 14px;
    margin-bottom: 4px;
}

.card-time {
    font-size: 12px;
    margin: 4px 0;
    opacity: 0.8;
}

.card-attendees {
    font-size: 12px;
    margin: 4px 0;
    opacity: 0.8;
}

.card-body {
    font-size: 12px;
    margin-top: 8px;
    opacity: 0.7;
}

.deadline-icon {
    display: flex;
    align-items: center;
    justify-content: center;
}

@media (max-width: 768px) {
    .intro {
        gap: 8px;
    }

    .controls {
        padding: 8px;
        gap: 6px;
        flex-direction: column;
        align-items: stretch;
    }

    .nav-arrows {
        display: flex;
        flex-direction: row;
        gap: 8px;
        width: 100%;
    }

    .nav-arrows > * {
        flex: 1;
    }

    .period-label {
        width: 100%;
        text-align: center;
        margin: 0;
        font-size: 16px;
        font-weight: 600;
    }

    .toggle-button {
        width: 100%;
    }

    .weekly-view {
        padding: 8px;
        gap: 12px;
    }

    .weekly-view h3 {
        font-size: 14px;
        padding: 8px 0;
    }

    .event-card {
        padding: 8px 10px;
        font-size: 13px;
        margin-bottom: 6px;
    }

    .card-title {
        font-size: 13px;
    }

    .card-time,
    .card-attendees,
    .card-body {
        font-size: 11px;
    }
}
</style>