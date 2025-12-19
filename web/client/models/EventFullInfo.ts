/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EventGroupReadShort } from './EventGroupReadShort';
import type { TaskWithoutEventRead } from './TaskWithoutEventRead';
export type EventFullInfo = {
    name: string;
    date: string;
    start_time: (string | null);
    end_time: (string | null);
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
    task_id?: (string | null);
    is_passed?: boolean;
    group?: (EventGroupReadShort | null);
    has_assigned_photographers?: boolean;
    exclude_admin_report?: boolean;
    task: TaskWithoutEventRead;
};

