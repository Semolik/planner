/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EventGroupReadShort } from './EventGroupReadShort';
export type EventRead = {
    name: string;
    date: string;
    start_time: string;
    end_time: string;
    name_approved?: boolean;
    location: string;
    link: string;
    organizer: string;
    required_photographers: number;
    group_id?: (string | null);
    description: string;
    id: string;
    level: string;
    level_id: string;
    is_passed?: boolean;
    group?: (EventGroupReadShort | null);
};

