<template>
    <div :class="['intro play-container', {'user-mode': !authStore.isAdmin}]">
        <div class="controls">
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
                    <div v-if="ev.body" class="card-body" v-html="ev.body" />

                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import {useRouter, useRoute} from 'vue-router';
import {watch, onMounted, ref, computed, nextTick} from 'vue';
import TuiCalendar from 'toast-ui-calendar-vue3';
import 'toast-ui-calendar-vue3/styles.css';
import {CalendarService} from '@/client';

const router = useRouter();
const route = useRoute();

const isSmallScreen = ref(false);
const calendarRef = ref();
const currentDate = ref(new Date());

const myEvents = ref([]);
const showTypedTasks = useLocalStorage('showTypedTasks', false);
const showCurrentUserTasks = useLocalStorage('showCurrentUserTasks', false);

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

// Формат даты YYYY-MM-DD
const formatDate = (d) => {
  return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2,'0')}-${d.getDate().toString().padStart(2,'0')}`;
}
// Формат месяца YYYY-MM
const formatMonth = (d) => {
  return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2,'0')}`;
}

// Получение начала и конца недели по дате (понедельник - воскресенье)
const getWeekStartEnd = (date) => {
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
      if (!isNaN(d)) {
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
    const groups = {};
    filteredEvents.value.forEach((ev) => {
        const dateKey = ev.start.split('T')[0];
        if (!groups[dateKey]) groups[dateKey] = [];
        groups[dateKey].push(ev);
    });
    return groups;
});

const sortedDates = computed(() => Object.keys(filteredGroupedByDate.value).sort());

const formatDateHeader = (dateStr) => {
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

        const allItems = [];
        for (const date in response) {
            response[date].forEach((calendarItem) => {
                allItems.push({date, item: calendarItem.item, type: calendarItem.item_type});
            });
        }

        const users = allItems.filter(i => i.type === 'user');
        const tasksWithEvents = allItems.filter(i => i.type === 'task' && i.item.event);
        const simpleTasks = allItems.filter(i => i.type === 'task' && !i.item.event);
        const typedTasks = allItems.filter(i => i.type === 'typed_task');
        const events = allItems.filter(i => i.type === 'event');

        tasksWithEvents.sort((a, b) => {
            const timeA = a.item.event.start_time;
            const timeB = b.item.event.start_time;
            return timeA.localeCompare(timeB);
        });

        const sortedItems = [...users, ...events, ...tasksWithEvents, ...simpleTasks, ...typedTasks];

        const newEvents = sortedItems.map((entry) => {
            const {date, item, type} = entry;
            let event = {
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
                event.title = item.name;
                event.start = `${date}T00:00:00`;
                event.end = `${date}T23:59:59`;
                event.category = 'allday';
                let users = [];
                for (const typedTask of item.typed_tasks) {
                    if (typedTask.task_states.length > 0) {
                        typedTask.task_states.forEach((state) => {
                            users.push(state.user);
                        });
                    }
                }
                event.attendees = users.length > 0 ? users.map((user) => user.first_name + " " + user.last_name) : null;
                event.users = users;
            } else if (type === 'typed_task') {
                event.attendees = item.task_states.length > 0 ? item.task_states.map((state) => state.user.first_name + " " + state.user.last_name) : null;
                event.users = item.task_states.length > 0 ? item.task_states.map((state) => state.user) : [];
                event.id = `task-${item.parent_task.id}`;
                event.category = 'allday';
                event.start = `${item.due_date}T00:00:00`;
                event.end = `${item.due_date}T23:59:59`;
                event.calendarId = item.task_type;
                let eventName = item.parent_task.name;
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

                const inProgress = item.task_states.some(state => state.state === 'pending');
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

                const photographers = [];
                let assignedPhotographersCount = 0;
                if (item.task && item.task.typed_tasks) {
                    const statusMap = {photographer: 'green', copywriter: 'green', designer: 'green'};
                    let users = [];
                    item.task.typed_tasks.forEach((typedTask) => {
                        if (typedTask.task_states.length > 0) {
                            typedTask.task_states.forEach((state) => {
                                users.push(state.user);
                            });
                        }
                        const has_pendingState = typedTask.task_states.some(state => state.state === 'pending');
                        const all_completed = typedTask.task_states.filter(state => state.state === 'completed').length > 0 &&
                            typedTask.task_states.every(typed_task => typed_task.state === 'completed' || typed_task.state === 'canceled');
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
                            const activeStates = typedTask.task_states.filter((state) => state.state !== 'canceled');
                            assignedPhotographersCount += activeStates.length;
                            typedTask.task_states.forEach((state) => {
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
                            circles += `<span style="display:inline-flex; padding: 1px 8px;border-radius: 10px;border: 1px solid black;align-items:center;gap:6px;${isSmallScreen.value?'background-color: black;color: white;':''}"><span style="width:12px;height:12px;border-radius:50%;background:${color};display:inline-block"></span>${label}</span>`;
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
                    const inProgress = typedTasks.some(tt => tt.task_states.some(s => s.state === 'pending'));
                    const isPastAnyDeadline = typedTasks.some(tt => tt.due_date_passed && (tt.task_states.some(s => s.state === 'pending') || tt.task_states.length == 0));

                    if (!item.has_assigned_photographers) {
                        event.backgroundColor = '#d3d3d3';
                        event.borderColor = '#6e6e6e';
                        event.color = '#3b3b3b';
                    } else if (item.task.all_typed_tasks_completed) {
                        event.backgroundColor = '#d3d3d3';
                        event.borderColor = '#6e6e6e';
                        event.color = '#3b3b3b';
                    } else if (inProgress && !isPastAnyDeadline) {
                        event.backgroundColor = '#ffd54f'; // Yellow for in progress
                        event.borderColor = '#cca800';
                        event.color = '#000000';
                    } else if (isPastAnyDeadline) {
                        event.backgroundColor = '#e94e4e'; // Red for overdue
                        event.borderColor = '#b53232';
                        event.color =isSmallScreen.value? 'black': 'white';
                        event.title = '! ' + event.title;
                    }
                } else {
                    event.backgroundColor = '#6cc24a'; // Green for active with photographers
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

onMounted(async () => {
    isSmallScreen.value = window.innerWidth < 768;

    setDateFromUrl();

    await nextTick();
    if (!isSmallScreen.value && calendarRef.value) {
        calendarRef.value.getInstance().setDate(currentDate.value);
    }
    fetchEvents();
});

watch([currentDate, isSmallScreen], () => {
    updateUrl();
});

window.addEventListener('resize', () => {
    const newIsSmall = window.innerWidth < 768;
    if (newIsSmall !== isSmallScreen.value) {
        isSmallScreen.value = newIsSmall;
        setDateFromUrl();
        if (!isSmallScreen.value && calendarRef.value) {
            calendarRef.value.getInstance().setDate(currentDate.value);
        }
        fetchEvents();
    }
});

function goToEvent(ev) {
    if (ev.id.startsWith('task-')) {
        const parts = ev.id.split('-');
        const typedTaskId = parts.slice(1).join('-');
        router.push({name: 'tasks-task_id', params: {task_id: typedTaskId}});
    } else if (ev.calendarId === 'photographer' || ev.title.startsWith('сдача репортажа')) {
        const typedTaskId = ev.id.split('-').slice(1).join('-');
        router.push({name: 'tasks-task_id', params: {task_id: typedTaskId}});
    }
}

const authStore = useAuthStore();

const handleClickEvent = (ev) => {
    if (!authStore.isAdmin) {
        goToEvent(ev.event);
    }
};

function handleCalendarUpdate(payload) {
    goToEvent(payload.event);
    return false;
}

const popupTemplates = ref({
    popupEdit: () => 'Редактировать',
    popupDelete: () => 'Удалить',
});

const options = computed(() => ({
    isReadOnly: true,
    usageStatistics: false,
    week: {
        startDayOfWeek: 1,
        dayNames: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
        showNowIndicator: true,
        showTimezoneCollapseButton: false,
        timezonesCollapsed: false,
        hourStart: 0,
        hourEnd: 24,
        eventView: ['time'],
        taskView: false,
        collapseDuplicateEvents: true,
    },
    month: {
        startDayOfWeek: 1,
        dayNames: ['вс', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб'],
        isAlways6Weeks: false,
    },
}));
</script>


<style lang="scss" scoped>
.user-mode {
    .toastui-calendar-section-button {
        display: none !important;
    }
}

.intro {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.controls {
    display: flex;
    margin-bottom: 10px;
    gap: 5px;
    @include md(true) {
        display: grid;
        grid-template-columns: repeat(2, 1fr);

        .period-label {
             font-size: var(--text-sm) !important;
            grid-column: 1 / -1;

        }
    }

    .period-label {
        border-radius: 10px;
        border: 1px solid black;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 3px 20px;
        font-size: 16px;
        color: #555;
        min-width: 200px;
    }
}

.my-calendar {
    width: 100%;
    height: 100%;
}

.weekly-view {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 0px;

    &.empty {

        height: calc(100% - 50px);
    }
}

.weekly-view h3 {
    font-size: 18px;
    margin: 0;
    color: #222;
    margin-bottom: 5px;
    margin-left: 5px;
}


.event-card {
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 5px;
    cursor: pointer;
    border: 1px solid #999999;
    background-color: white;
    color: #000000;

    .deadline-icon {
        margin-left: 5px;
        vertical-align: middle;
        color: $text-color;
        width: 18px;
        height: 18px;
        margin-top: 3px;
    }
}

.card-title {
    font-weight: bold;
}

.card-time {
    font-size: 14px;
    color: inherit;
}

.card-attendees {
    font-size: 14px;
    color: inherit;
}
.card-body {
    margin-top: 5px;
    font-size: 14px;
    display: flex;
    flex-direction: column;
    gap: 5px;
}
</style>
