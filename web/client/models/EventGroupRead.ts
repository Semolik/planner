/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EventFullInfo } from './EventFullInfo';
import type { TaskReadShortWithoutEvent } from './TaskReadShortWithoutEvent';
export type EventGroupRead = {
    name: string;
    description: string;
    organizer: string;
    link: string;
    id: string;
    events_count: number;
    period_start?: (string | null);
    period_end?: (string | null);
    aggregate_task?: (TaskReadShortWithoutEvent | null);
    events: Array<EventFullInfo>;
};

