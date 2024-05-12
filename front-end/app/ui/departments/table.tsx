import { Department, Employee } from "@/app/lib/definitions";
import { ViewEmployees } from "./buttons";

export default async function DepartmentTable({
  departments,
}: {
  departments: Department[];
}) {
  return (
    <div className="mt-6 flow-root">
      <div className="inline-block min-w-full align-middle">
        <div className="rounded-lg bg-gray-50 p-2 md:pt-0">
          <table className="hidden min-w-full text-gray-900 md:table">
            <thead className="rounded-lg text-left text-sm font-normal">
              <tr>
                <th scope="col" className="px-3 py-5 font-medium sm:pl-6">
                  DepartmentID
                </th>
                <th scope="col" className="px-3 py-5 font-medium">
                  Name
                </th>
                <th scope="col" className="px-3 py-5 font-medium">
                  Phone
                </th>
                <th scope="col" className="px-3 py-5 font-medium">
                  Location
                </th>
                <th scope="col" className="px-3 py-5 font-medium">
                  Budget
                </th>
                <th scope="col" className="px-3 py-5 font-medium">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white">
              {departments?.map((department, i) => (
                <tr
                  key={i}
                  className="h-12 w-full border-b py-3 text-sm last-of-type:border-none [&:first-child>td:first-child]:rounded-tl-lg [&:first-child>td:last-child]:rounded-tr-lg [&:last-child>td:first-child]:rounded-bl-lg [&:last-child>td:last-child]:rounded-br-lg"
                >
                  <td className="whitespace-nowrap px-3 py-3">
                    {department.id}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3">
                    {department.name}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3">
                    {department.phone}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3">
                    {department.location}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3">
                    {department.budget}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3">
                    <ViewEmployees id={department.id} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export async function DepartmentWithEmployeesTable({
  employees,
}: {
  employees: Employee[];
}) {
  return (
    <div className="mt-6 flow-root">
      <div className="inline-block min-w-full align-middle">
        <div className="rounded-lg bg-gray-50 p-2 md:pt-0">
          <table className="hidden min-w-full text-gray-900 md:table">
            <thead className="rounded-lg text-left text-sm font-normal">
              <tr>
                <th scope="col" className="px-3 py-5 font-medium sm:pl-6">
                  EmployeeID
                </th>
                <th scope="col" className="px-3 py-5 font-medium">
                  DepartmentID
                </th>
                <th scope="col" className="px-3 py-5 font-medium">
                  Name
                </th>
                <th scope="col" className="px-3 py-5 font-medium">
                  Age
                </th>
                <th scope="col" className="px-3 py-5 font-medium">
                  Position
                </th>
              </tr>
            </thead>
            <tbody className="bg-white">
              {employees?.map((employee, i) => (
                <tr
                  key={i}
                  className="h-12 w-full border-b py-3 text-sm last-of-type:border-none [&:first-child>td:first-child]:rounded-tl-lg [&:first-child>td:last-child]:rounded-tr-lg [&:last-child>td:first-child]:rounded-bl-lg [&:last-child>td:last-child]:rounded-br-lg"
                >
                  <td className="whitespace-nowrap px-3 py-3">{employee.id}</td>
                  <td className="whitespace-nowrap px-3 py-3">
                    {employee.departmentId}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3">
                    {employee.name}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3">
                    {employee.age}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3">
                    {employee.position}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
