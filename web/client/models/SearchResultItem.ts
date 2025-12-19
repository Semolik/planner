/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EventGroupReadShort } from './EventGroupReadShort';
import type { EventRead } from './EventRead';
import type { TaskRead } from './TaskRead';
import type { UserReadShort } from './UserReadShort';
/**
 * Единый результат поиска с типом и данными
 */
export type SearchResultItem = {
    type: SearchResultItem.type;
    data: (TaskRead | EventRead | EventGroupReadShort | UserReadShort);
};
export namespace SearchResultItem {
    export enum type {
        TASK = 'task',
        EVENT = 'event',
        GROUP = 'group',
        USER = 'user',
    }
}

