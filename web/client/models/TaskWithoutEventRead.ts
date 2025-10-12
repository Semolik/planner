/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TypedTaskRead } from './TypedTaskRead';
export type TaskWithoutEventRead = {
    event_id?: (string | null);
    name: string;
    id: string;
    all_typed_tasks_completed: boolean;
    typed_tasks: Array<TypedTaskRead>;
};

