/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TypedTaskRead } from './TypedTaskRead';
import type { UserReadShort } from './UserReadShort';
export type TaskWithoutEventRead = {
    event_id?: (string | null);
    name?: (string | null);
    use_in_pgas: boolean;
    id: string;
    all_typed_tasks_completed: boolean;
    displayed_name?: (string | null);
    birthday_user?: (UserReadShort | null);
    typed_tasks: Array<TypedTaskRead>;
};

