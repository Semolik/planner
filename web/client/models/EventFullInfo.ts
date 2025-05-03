/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TaskWithoutEventRead } from './TaskWithoutEventRead';
export type EventFullInfo = {
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
    task: TaskWithoutEventRead;
};

