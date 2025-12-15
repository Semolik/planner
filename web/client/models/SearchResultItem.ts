/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SearchEventData } from './SearchEventData';
import type { SearchGroupData } from './SearchGroupData';
import type { SearchTaskData } from './SearchTaskData';
import type { SearchUserData } from './SearchUserData';
/**
 * Единый результат поиска с типом и данными
 */
export type SearchResultItem = {
    type: SearchResultItem.type;
    data: (SearchTaskData | SearchEventData | SearchGroupData | SearchUserData);
};
export namespace SearchResultItem {
    export enum type {
        TASK = 'task',
        EVENT = 'event',
        GROUP = 'group',
        USER = 'user',
    }
}

