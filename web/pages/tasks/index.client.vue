<template>
  <div class="intro play-container">
    <div class="controls">
      <app-button active @click="prev">
        <Icon name="mdi:arrow-left"/>
      </app-button>

      <app-button @click="next" active>
        <Icon name="mdi:arrow-right"/>
      </app-button>
      <div class="period-label">
        {{ periodLabel }}
      </div>
    </div>
    <TuiCalendar class="my-calendar" ref="calendarRef" view="month" @beforeCreateEvent="createEvent"
                 @beforeUpdateEvent="handleUpdateEvent" :use-detail-popup="true" :week="options.week"
                 :month="options.month" :calendars="calendars" :events="myEvents" :template="popupTemplates"
                 isReadOnly :options="options"
    />
  </div>
</template>

<script setup lang="ts">
import TuiCalendar, {Calendar} from 'toast-ui-calendar-vue3';
import 'toast-ui-calendar-vue3/styles.css';
import {CalendarService} from '@/client';
import {computed, ref, onMounted} from 'vue';
import {useRouter} from 'vue-router';

const router = useRouter();

const calendarRef = ref<Calendar | undefined>();
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
    backgroundColor: '#00ff0061',
    borderColor: '#00ff0061',
    dragBackgroundColor: '#00ff0061',
  },
]);


const currentCalendarDate = ref(new Date());


const periodLabel = computed(() => {
  const date = currentCalendarDate.value;
  const monthName = date.toLocaleString('ru-RU', {month: 'long'});
  const year = date.getFullYear();


  return `${monthName.charAt(0).toUpperCase() + monthName.slice(1)} ${year}`;
});

const fetchEvents = async () => {
  if (!calendarRef.value) return;

  const instance = calendarRef.value.getInstance();
  const view = instance.getViewName();
  const currentDate = instance.getDate().toDate();

  let dateFrom, dateTo;
  if (view === 'month') {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth() + 1;
    dateFrom = `${year}-${month.toString().padStart(2, '0')}-01`;
    const lastDay = new Date(year, month, 0).getDate();
    dateTo = `${year}-${month.toString().padStart(2, '0')}-${lastDay.toString().padStart(2, '0')}`;
  } else if (view === 'week') {
    const day = currentDate.getDay();
    const diff = (day === 0 ? -6 : 1 - day);
    const startWeek = new Date(currentDate);
    startWeek.setDate(startWeek.getDate() + diff);
    dateFrom = formatDate(startWeek);
    const endWeek = new Date(startWeek);
    endWeek.setDate(endWeek.getDate() + 6);
    dateTo = formatDate(endWeek);
  } else if (view === 'day') {
    dateFrom = formatDate(currentDate);
    dateTo = dateFrom;
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


    const newEvents = sortedItems.map((entry, index) => {
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
      console.log(type);
      if (type === 'user') {
        event.title = `День рождения: ${item.first_name} ${item.last_name}`;
        event.start = `${date}T00:00:00`;
        event.end = `${date}T23:59:59`;
        event.category = 'allday';
      } else if (type === 'task') {
        if (item.event) {
          console.log(item.event);
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
          console.log(item.task_type);
          if (item.task_type === 'photographer') {
            event.title = `сдача репортажа "${eventName}"`;

            event.backgroundColor = '#d3d3d3';
            event.borderColor = '#a9a9a9';
            event.color = '#202020';
          } else if (item.task_type === 'copywriter') {
            event.title = `текст публикации к мероприятию "${eventName}"`;
          } else if (item.task_type === 'designer') {
            event.title = `обложка на альбом "${eventName}"`;
          }
        } else {
          event.title = eventName;
        }
        if (!event.attendees && (item.parent_task.event ? !item.parent_task.event.is_passed : false)) {
          event.backgroundColor = 'red';
          event.borderColor = 'black';
          event.color = 'white';
          event.title = '! ' + event.title;
        }

        event.body = item.description;
      } else if (type === 'event') {
        event.title = `Репортаж: ${item.name}`;
        event.start = `${item.date}T${item.start_time}`;
        event.end = `${item.date}T${item.end_time}`;
        event.category = 'allday';


        event.backgroundColor = '#00ff0061';
        event.borderColor = '#00ff0061';
        event.dragBackgroundColor = '#00ff0061';
        event.color = 'black';


        const photographers = [];
        if (item.task && item.task.typed_tasks) {
          item.task.typed_tasks.forEach((typedTask) => {
            if (typedTask.task_type === 'photographer' && typedTask.task_states) {
              typedTask.task_states.forEach((state) => {
                photographers.push(state.user.first_name + " " + state.user.last_name);
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
              assignedPhotographersCount += typedTask.task_states?.length ?? 0;
            }
          });
        }

        if (!isEventPassed && assignedPhotographersCount < requiredPhotographers) {
          event.backgroundColor = 'red';
          event.borderColor = 'black';
          event.color = 'white';
          event.title = '! ' + event.title;
        }
      }

      return event;
    });

    myEvents.value = newEvents;
  } catch (error) {
    console.error('Ошибка при получении данных календаря:', error);
  }
};

const formatDate = (d: Date) => {
  return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`;
};

const next = () => {
  if (calendarRef.value) {
    const instance = calendarRef.value.getInstance();
    instance.next();
    currentCalendarDate.value = instance.getDate().toDate();
    fetchEvents();
  }
};

const prev = () => {
  if (calendarRef.value) {
    const instance = calendarRef.value.getInstance();
    instance.prev();
    currentCalendarDate.value = instance.getDate().toDate();
    fetchEvents();
  }
};

onMounted(() => {
  if (calendarRef.value) {
    currentCalendarDate.value = calendarRef.value.getInstance().getDate().toDate();
    fetchEvents();
  }
});

function createEvent(event) {
  myEvents.value.push(event);
}

function handleUpdateEvent(payload) {
  console.log('Event clicked:', payload);
  if (payload.event.id.startsWith('task-')) {
    const parts = payload.event.id.split('-');

    const typedTaskId = parts.slice(1).join('-');
    console.log('Typed Task ID:', typedTaskId);
    router.push({name: 'tasks-task_id', params: {task_id: typedTaskId}});
  } else if (payload.event.calendarId === 'photographer' || payload.event.title.startsWith('сдача репортажа')) {

    const typedTaskId = payload.event.id.split('-').slice(1).join('-');
    router.push({name: 'tasks-task_id', params: {task_id: typedTaskId}});
  }
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

<style scoped lang="scss">
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
</style>

<style>
.my-calendar {
  width: 100%;
  height: 100%;
}
</style>
