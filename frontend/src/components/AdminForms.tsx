import type {
  AuthUser,
  Department,
  Faculty,
  LocationGuide,
  StaffMember,
} from "../types";
import type { UserDraft } from "./forms";
import { splitCsv, toCsv } from "./forms";

export function FacultyForm({
  draft,
  onChange,
  disabled,
}: {
  draft: Faculty;
  onChange: (draft: Faculty) => void;
  disabled: boolean;
}) {
  return (
    <div className="form-grid">
      <input
        className="input"
        value={draft.id}
        disabled={disabled}
        onChange={(event) => onChange({ ...draft, id: event.target.value })}
        placeholder="faculty id"
      />
      <input
        className="input"
        value={draft.name}
        disabled={disabled}
        onChange={(event) => onChange({ ...draft, name: event.target.value })}
        placeholder="Faculty name"
      />
      <input
        className="input"
        value={draft.short_name ?? ""}
        disabled={disabled}
        onChange={(event) =>
          onChange({ ...draft, short_name: event.target.value })
        }
        placeholder="Short name"
      />
      <input
        className="input"
        value={draft.campus ?? ""}
        disabled={disabled}
        onChange={(event) => onChange({ ...draft, campus: event.target.value })}
        placeholder="Campus"
      />
      <textarea
        className="input input--wide"
        value={draft.description ?? ""}
        disabled={disabled}
        onChange={(event) =>
          onChange({ ...draft, description: event.target.value })
        }
        placeholder="Description"
        rows={3}
      />
    </div>
  );
}

export function DepartmentForm({
  draft,
  onChange,
  faculties,
  disabled,
}: {
  draft: Department;
  onChange: (draft: Department) => void;
  faculties: Faculty[];
  disabled: boolean;
}) {
  return (
    <div className="form-grid">
      <input
        className="input"
        value={draft.id}
        disabled={disabled}
        onChange={(event) => onChange({ ...draft, id: event.target.value })}
        placeholder="department id"
      />
      <select
        className="input"
        value={draft.faculty_id ?? ""}
        disabled={disabled}
        onChange={(event) =>
          onChange({
            ...draft,
            faculty_id: event.target.value === "" ? null : event.target.value,
          })
        }
      >
        <option value="">No faculty</option>
        {faculties.map((faculty) => (
          <option key={faculty.id} value={faculty.id}>
            {faculty.name}
          </option>
        ))}
      </select>
      <input
        className="input"
        value={draft.name}
        disabled={disabled}
        onChange={(event) => onChange({ ...draft, name: event.target.value })}
        placeholder="Department name"
      />
      <input
        className="input"
        value={draft.campus ?? ""}
        disabled={disabled}
        onChange={(event) => onChange({ ...draft, campus: event.target.value })}
        placeholder="Campus"
      />
      <input
        className="input input--wide"
        value={toCsv(draft.aliases)}
        disabled={disabled}
        onChange={(event) =>
          onChange({ ...draft, aliases: splitCsv(event.target.value) })
        }
        placeholder="Aliases (comma separated)"
      />
      <textarea
        className="input input--wide"
        value={draft.location_guide ?? ""}
        disabled={disabled}
        onChange={(event) =>
          onChange({ ...draft, location_guide: event.target.value })
        }
        placeholder="Location guide"
        rows={3}
      />
      <textarea
        className="input input--wide"
        value={draft.notes ?? ""}
        disabled={disabled}
        onChange={(event) => onChange({ ...draft, notes: event.target.value })}
        placeholder="Notes"
        rows={3}
      />
    </div>
  );
}

export function StaffForm({
  draft,
  onChange,
  departments,
  faculties,
  disabled,
}: {
  draft: StaffMember;
  onChange: (draft: StaffMember) => void;
  departments: Department[];
  faculties: Faculty[];
  disabled: boolean;
}) {
  return (
    <div className="form-grid">
      <input
        className="input"
        value={draft.id}
        disabled={disabled}
        onChange={(event) => onChange({ ...draft, id: event.target.value })}
        placeholder="staff id"
      />
      <input
        className="input"
        value={draft.full_name}
        disabled={disabled}
        onChange={(event) =>
          onChange({ ...draft, full_name: event.target.value })
        }
        placeholder="Full name"
      />
      <input
        className="input"
        value={draft.title ?? ""}
        disabled={disabled}
        onChange={(event) => onChange({ ...draft, title: event.target.value })}
        placeholder="Title"
      />
      <input
        className="input"
        value={draft.rank_role ?? ""}
        disabled={disabled}
        onChange={(event) =>
          onChange({ ...draft, rank_role: event.target.value })
        }
        placeholder="Role"
      />
      <select
        className="input"
        value={draft.faculty_id ?? ""}
        disabled={disabled}
        onChange={(event) =>
          onChange({
            ...draft,
            faculty_id: event.target.value === "" ? null : event.target.value,
          })
        }
      >
        <option value="">No faculty</option>
        {faculties.map((faculty) => (
          <option key={faculty.id} value={faculty.id}>
            {faculty.name}
          </option>
        ))}
      </select>
      <select
        className="input"
        value={draft.department_id ?? ""}
        disabled={disabled}
        onChange={(event) =>
          onChange({
            ...draft,
            department_id:
              event.target.value === "" ? null : event.target.value,
          })
        }
      >
        <option value="">No department</option>
        {departments.map((department) => (
          <option key={department.id} value={department.id}>
            {department.name}
          </option>
        ))}
      </select>
      <input
        className="input"
        value={draft.campus ?? ""}
        disabled={disabled}
        onChange={(event) => onChange({ ...draft, campus: event.target.value })}
        placeholder="Campus"
      />
      <input
        className="input input--wide"
        value={toCsv(draft.specializations)}
        disabled={disabled}
        onChange={(event) =>
          onChange({ ...draft, specializations: splitCsv(event.target.value) })
        }
        placeholder="Specializations (comma separated)"
      />
      <input
        className="input input--wide"
        value={toCsv(draft.aliases)}
        disabled={disabled}
        onChange={(event) =>
          onChange({ ...draft, aliases: splitCsv(event.target.value) })
        }
        placeholder="Aliases (comma separated)"
      />
      <textarea
        className="input input--wide"
        value={draft.bio ?? ""}
        disabled={disabled}
        onChange={(event) => onChange({ ...draft, bio: event.target.value })}
        placeholder="Bio"
        rows={4}
      />
      <textarea
        className="input input--wide"
        value={draft.source_notes ?? ""}
        disabled={disabled}
        onChange={(event) =>
          onChange({ ...draft, source_notes: event.target.value })
        }
        placeholder="Source notes"
        rows={3}
      />
    </div>
  );
}

export function LocationForm({
  draft,
  onChange,
  faculties,
  departments,
  disabled,
}: {
  draft: LocationGuide;
  onChange: (draft: LocationGuide) => void;
  faculties: Faculty[];
  departments: Department[];
  disabled: boolean;
}) {
  return (
    <div className="form-grid">
      <input
        className="input"
        value={draft.id}
        disabled={disabled}
        onChange={(event) => onChange({ ...draft, id: event.target.value })}
        placeholder="guide id"
      />
      <select
        className="input"
        value={draft.faculty_id ?? ""}
        disabled={disabled}
        onChange={(event) =>
          onChange({
            ...draft,
            faculty_id: event.target.value === "" ? null : event.target.value,
          })
        }
      >
        <option value="">No faculty</option>
        {faculties.map((faculty) => (
          <option key={faculty.id} value={faculty.id}>
            {faculty.name}
          </option>
        ))}
      </select>
      <select
        className="input"
        value={draft.department_id ?? ""}
        disabled={disabled}
        onChange={(event) =>
          onChange({
            ...draft,
            department_id:
              event.target.value === "" ? null : event.target.value,
          })
        }
      >
        <option value="">No department</option>
        {departments.map((department) => (
          <option key={department.id} value={department.id}>
            {department.name}
          </option>
        ))}
      </select>
      <input
        className="input"
        value={draft.campus ?? ""}
        disabled={disabled}
        onChange={(event) => onChange({ ...draft, campus: event.target.value })}
        placeholder="Campus"
      />
      <textarea
        className="input input--wide"
        value={draft.directions_text}
        disabled={disabled}
        onChange={(event) =>
          onChange({ ...draft, directions_text: event.target.value })
        }
        placeholder="Directions"
        rows={4}
      />
    </div>
  );
}

export function UserForm({
  draft,
  onChange,
  disabled,
}: {
  draft: UserDraft;
  onChange: (draft: UserDraft) => void;
  disabled: boolean;
}) {
  return (
    <div className="form-grid">
      <input
        className="input"
        value={draft.full_name}
        disabled={disabled}
        onChange={(event) =>
          onChange({ ...draft, full_name: event.target.value })
        }
        placeholder="Full name"
      />
      <input
        className="input"
        value={draft.email}
        disabled={disabled}
        onChange={(event) => onChange({ ...draft, email: event.target.value })}
        placeholder="Email"
      />
      <select
        className="input"
        value={draft.role}
        disabled={disabled}
        onChange={(event) =>
          onChange({ ...draft, role: event.target.value as AuthUser["role"] })
        }
      >
        <option value="viewer">viewer</option>
        <option value="editor">editor</option>
        <option value="super_admin">super_admin</option>
      </select>
      <input
        className="input"
        type="password"
        value={draft.password}
        disabled={disabled}
        onChange={(event) =>
          onChange({ ...draft, password: event.target.value })
        }
        placeholder="Password"
      />
    </div>
  );
}
