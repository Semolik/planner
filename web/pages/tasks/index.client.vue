<template>
    <div class="intro play-container">
        <div class="controls">
            <app-button active @click="prev">
                <Icon name="mdi:arrow-left"/>
            </app-button>

            <app-button active @click="next">
                <Icon name="mdi:arrow-right"/>
            </app-button>
            <div class="period-label">
                {{ periodLabel }}
            </div>
        </div>
        <TuiCalendar
            v-if="!isSmallScreen"
            ref="calendarRef"
            :calendars="calendars"
            :events="myEvents"
            :month="options.month"
            :options="options"
            :template="popupTemplates"
            :use-detail-popup="true"
            :week="options.week"
            class="my-calendar"
            isReadOnly
            view="month"
            @beforeCreateEvent="createEvent"
            @beforeUpdateEvent="handleCalendarUpdate"
        />
        <div v-else class="weekly-view">
            <div v-for="(dateKey, index) in sortedDates" :key="index">
                <h3>{{ formatDateHeader(dateKey) }}</h3>
                <hr>
                <div
                    v-for="ev in groupedByDate[dateKey]"
                    :key="ev.id"
                    :style="{
            backgroundColor: ev.backgroundColor,
            border: `1px solid ${ev.borderColor}`,
            color: ev.color
          }"
                    class="event-card"
                    @click="handleEventClick(ev)"
                >
                    <div class="card-title">{{ ev.title }}</div>
                    <div v-if="ev.category === 'time'" class="card-time">
                        {{ ev.start.split('T')[1].slice(0, 5) }} - {{ ev.end.split('T')[1].slice(0, 5) }}
                    </div>
                    <div v-if="ev.attendees" class="card-attendees">
                        Участники: {{ ev.attendees.join(', ') }}
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import TuiCalendar from 'toast-ui-calendar-vue3';
import 'toast-ui-calendar-vue3/styles.css';
import { CalendarService } from '@/client';
import { computed, ref, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useNuxtApp } from 'nuxt/app';

const { $viewport } = useNuxtApp();
const isSmallScreen = computed(() => $viewport.isLessThan('md'));

const router = useRouter();
const calendarRef = ref();
const myEvents = ref([]);
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

const currentDate = ref(new Date());

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

const groupedByDate = computed(() => {
    const groups = {};
    myEvents.value.forEach((ev) => {
        const dateKey = ev.start.split('T')[0];
        if (!groups[dateKey]) groups[dateKey] = [];
        groups[dateKey].push(ev);
    });
    return groups;
});

const sortedDates = computed(() => Object.keys(groupedByDate.value).sort());

const formatDateHeader = (dateStr) => {
    const d = new Date(dateStr);
    return d.toLocaleString('ru-RU', {weekday: 'long', day: 'numeric', month: 'long'});
};

const fetchEvents = async () => {
    let view;
    let currentViewDate;
    if (!isSmallScreen.value && calendarRef.value) {
        const instance = calendarRef.value.getInstance();
        view = instance.getViewName();
        currentViewDate = instance.getDate().toDate();
    } else {
        view = 'week';
        currentViewDate = currentDate.value;
    }

    let dateFrom, dateTo;
    if (view === 'month') {
        const year = currentViewDate.getFullYear();
        const month = currentViewDate.getMonth() + 1;
        dateFrom = `${year}-${month.toString().padStart(2, '0')}-01`;
        const lastDay = new Date(year, month, 0).getDate();
        dateTo = `${year}-${month.toString().padStart(2, '0')}-${lastDay.toString().padStart(2, '0')}`;
    } else if (view === 'week') {
        const day = currentViewDate.getDay();
        const diff = (day === 0 ? 6 : day - 1);
        const startWeek = new Date(currentViewDate);
        startWeek.setDate(startWeek.getDate() - diff);
        dateFrom = formatDate(startWeek);
        const endWeek = new Date(startWeek);
        endWeek.setDate(endWeek.getDate() + 6);
        dateTo = formatDate(endWeek);
    } else {
        return;
    }

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
            };
            if (type === 'user') {
                event.title = `День рождения: ${item.first_name} ${item.last_name}`;
                event.start = `${date}T00:00:00`;
                event.end = `${date}T23:59:59`;
                event.category = 'allday';
            } else if (type === 'task') {
                if (item.event) {
                    const eventDate = item.event.date;
                    event.title = item.name;
                    event.start = `${eventDate}T${item.event.start_time}`;
                    event.end = `${eventDate}T${item.event.end_time}`;
                    event.category = 'time';
                } else {
                    event.title = item.name;
                    event.start = `${date}T00:00:00`;
                    event.end = `${date}T23:59:59`;
                    event.category = 'allday';
                }
            } else if (type === 'typed_task') {
                event.attendees = item.task_states.length > 0 ? item.task_states.map((state) => state.user.first_name + " " + state.user.last_name) : null;
                event.id = `task-${item.parent_task.id}`;
                event.category = 'allday';
                event.start = `${item.due_date}T00:00:00`;
                event.end = `${item.due_date}T23:59:59`;
                event.calendarId = item.task_type;
                let eventName = item.parent_task.name;
                if (item.parent_task.event) {
                    eventName = item.parent_task.event.name;
                    if (item.task_type === 'photographer') {
                        event.title = `сдача репортажа "${eventName}"`;
                        event.backgroundColor = '#d3d3d3';
                        event.borderColor = '#6e6e6e';
                        event.color = '#3b3b3b';
                    } else if (item.task_type === 'copywriter') {
                        event.title = `текст публикации к мероприятию "${eventName}"`;
                    } else if (item.task_type === 'designer') {
                        event.title = `обложка на альбом "${eventName}"`;
                    }
                } else {
                    event.title = eventName;
                }

                const isPastDeadline = new Date(item.due_date) < new Date();
                const assignedUsers = item.task_states.filter(state => state.state !== 'canceled');
                const hasAssigned = assignedUsers.length > 0;
                const allCompleted = assignedUsers.every(state => state.state === 'completed');
                const inProgress = assignedUsers.some(state => state.state === 'pending');

                let eventInProgress = false;
                if (item.parent_task.event && !item.parent_task.event.is_passed) {
                    const photographerTasks = item.parent_task.event.task?.typed_tasks?.filter(t => t.task_type === 'photographer') || [];
                    eventInProgress = photographerTasks.some(t => t.task_states.some(s => s.state !== 'canceled'));
                }

                if (eventInProgress) {
                    if (!hasAssigned) {
                        event.backgroundColor = '#e94e4e';
                        event.borderColor = '#b53232';
                        event.color = '#ffffff';
                        event.title = '! ' + event.title;
                    } else if (hasAssigned && !isPastDeadline) {
                        event.backgroundColor = '#4a90e2';
                        event.borderColor = '#357abd';
                        event.color = '#ffffff';
                    } else if (hasAssigned && isPastDeadline) {
                        event.backgroundColor = '#e94e4e';
                        event.borderColor = '#b53232';
                        event.color = '#ffffff';
                        event.title = '! ' + event.title;
                    }
                } else {
                    if (!hasAssigned || allCompleted) {
                        event.backgroundColor = '#d3d3d3';
                        event.borderColor = '#6e6e6e';
                        event.color = '#3b3b3b';
                    } else if (inProgress) {
                        event.backgroundColor = '#4a90e2';
                        event.borderColor = '#357abd';
                        event.color = '#ffffff';
                    } else if (isPastDeadline) {
                        event.backgroundColor = '#e94e4e';
                        event.borderColor = '#b53232';
                        event.color = '#ffffff';
                        event.title = '! ' + event.title;
                    }
                }
                event.body = item.description;
            } else if (type === 'event') {
                event.title = item.name;
                event.start = `${item.date}T${item.start_time}`;
                event.end = `${item.date}T${item.end_time}`;
                event.category = 'allday';
                event.backgroundColor = '#6cc24a61';
                event.borderColor = '#52923561';
                event.dragBackgroundColor = '#6cc24a61';
                event.color = '#000000';

                const photographers = [];
                if (item.task && item.task.typed_tasks) {
                    item.task.typed_tasks.forEach((typedTask) => {
                        if (typedTask.task_type === 'photographer' && typedTask.task_states) {
                            typedTask.task_states.forEach((state) => {
                                if (state.state !== 'canceled') {
                                    photographers.push(state.user.first_name + " " + state.user.last_name);
                                }
                            });
                        }
                    });
                }
                event.attendees = photographers.length > 0 ? photographers : null;

                const isEventPassed = item.is_passed ?? false;
                const requiredPhotographers = item.required_photographers ?? 0;
                let assignedPhotographersCount = 0;
                if (item.task && item.task.typed_tasks) {
                    item.task.typed_tasks.forEach((typedTask) => {
                        if (typedTask.task_type === 'photographer') {
                            assignedPhotographersCount += typedTask.task_states?.filter(s => s.state !== 'canceled').length ?? 0;
                        }
                    });
                }

                if (isEventPassed) {
                    const typedTasks = item.task?.typed_tasks || [];
                    const assignedTyped = typedTasks.some(tt => tt.task_states?.some(s => s.state !== 'canceled'));
                    const allCompleted = typedTasks.every(tt => tt.task_states.every(s => s.state === 'completed' || s.state === 'canceled'));
                    const inProgress = typedTasks.some(tt => tt.task_states.some(s => s.state === 'pending'));
                    const isPastAnyDeadline = typedTasks.some(tt => new Date(tt.due_date) < new Date());

                    if (!assignedTyped || allCompleted) {
                        event.backgroundColor = '#d3d3d3';
                        event.borderColor = '#6e6e6e';
                        event.color = '#3b3b3b';
                    } else if (inProgress) {
                        event.backgroundColor = '#4a90e2';
                        event.borderColor = '#357abd';
                        event.color = '#ffffff';
                    } else if (isPastAnyDeadline) {
                        event.backgroundColor = '#e94e4e';
                        event.borderColor = '#b53232';
                        event.color = '#ffffff';
                        event.title = '! ' + event.title;
                    }
                } else {
                    if (assignedPhotographersCount < requiredPhotographers) {
                        event.backgroundColor = '#e94e4e';
                        event.borderColor = '#b53232';
                        event.color = '#ffffff';
                        event.title = '! ' + event.title;
                    }
                }
            }
            return event;
        });

        myEvents.value = newEvents;
    } catch (error) {
        console.error('Ошибка при получении данных календаря:', error);
    }
};

const formatDate = (d) => {
    return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`;
};

const next = () => {
    if (!isSmallScreen.value && calendarRef.value) {
        const instance = calendarRef.value.getInstance();
        instance.next();
        currentDate.value = instance.getDate().toDate();
    } else {
        currentDate.value = new Date(currentDate.value.setDate(currentDate.value.getDate() + 7));
    }
    fetchEvents();
};

const prev = () => {
    if (!isSmallScreen.value && calendarRef.value) {
        const instance = calendarRef.value.getInstance();
        instance.prev();
        currentDate.value = instance.getDate().toDate();
    } else {
        currentDate.value = new Date(currentDate.value.setDate(currentDate.value.getDate() - 7));
    }
    fetchEvents();
};

onMounted(async () => {
    await nextTick();
    if (!isSmallScreen.value && calendarRef.value) {
        currentDate.value = calendarRef.value.getInstance().getDate().toDate();
    }
    fetchEvents();
});

function createEvent(event) {
    myEvents.value.push(event);
}

function handleEventClick(ev) {
    console.log('Event clicked:', ev);
    if (ev.id.startsWith('task-')) {
        const parts = ev.id.split('-');
        const typedTaskId = parts.slice(1).join('-');
        console.log('Typed Task ID:', typedTaskId);
        router.push({name: 'tasks-task_id', params: {task_id: typedTaskId}});
    } else if (ev.calendarId === 'photographer' || ev.title.startsWith('сдача репортажа')) {
        const typedTaskId = ev.id.split('-').slice(1).join('-');
        router.push({name: 'tasks-task_id', params: {task_id: typedTaskId}});
    }
}

function handleCalendarUpdate(payload) {
    handleEventClick(payload.event);
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
.intro {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.controls {
    display: flex;
    margin-bottom: 10px;
    gap: 5px;

    .period-label {
        border-radius: 10px;
        border: 1px solid black;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 3px 20px;
        font-size: 16px;
        color: $text-color-secondary;
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
    gap: 20px;
    padding: 10px;
    overflow-y: auto;
    height: calc(100% - 50px); /* Adjust for controls */
}

.weekly-view h3 {
    font-size: 18px;
    margin: 0;
    color: $text-color;
}

.weekly-view hr {
    border: 0;
    border-top: 1px solid $border-color;
    margin: 10px 0;
}

.event-card {
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 10px;
    cursor: pointer;
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
</style>
