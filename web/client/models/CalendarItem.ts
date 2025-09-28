/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EventFullInfo } from './EventFullInfo';
import type { TaskReadShort } from './TaskReadShort';
import type { TypedTaskReadFull } from './TypedTaskReadFull';
import type { UserReadShort } from './UserReadShort';
export type CalendarItem = {
    item: (TypedTaskReadFull | TaskReadShort | UserReadShort | EventFullInfo);
    item_type: CalendarItem.item_type;
};
export namespace CalendarItem {
    export enum item_type {
        TASK = 'task',
        USER = 'user',
        TYPED_TASK = 'typed_task',
        EVENT = 'event',
    }
}

