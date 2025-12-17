/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EventRead } from './EventRead';
import type { UserReadShort } from './UserReadShort';
export type TaskReadShort = {
    event_id?: (string | null);
    name?: (string | null);
    use_in_pgas: boolean;
    id: string;
    all_typed_tasks_completed: boolean;
    displayed_name?: (string | null);
    birthday_user?: (UserReadShort | null);
    event?: (EventRead | null);
};

