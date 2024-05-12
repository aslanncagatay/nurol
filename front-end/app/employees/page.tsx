import Table from "@/app/ui/employees/table";
import { CreateEmployee } from "../ui/employees/buttons";
import { lusitana } from "@/app/ui/fonts";
import { DepartmentsTableSkeleton } from "@/app/ui/skeletons";
import { Suspense } from "react";
import { Metadata } from "next";
import { getEmployees } from "../lib/api/employees";

export const metadata: Metadata = {
  title: "Employees",
};

export default async function Page() {
  const employees = await getEmployees();

  return (
    <div className="w-full">
      <div className="flex w-full items-center justify-between">
        <h1 className={`${lusitana.className} text-2xl`}>Employees</h1>
      </div>
      <div className="mt-4 flex items-center justify-end gap-2 md:mt-8">
        <CreateEmployee />
      </div>
      <Suspense key={"employees"} fallback={<DepartmentsTableSkeleton />}>
        <Table employees={employees} />
      </Suspense>
    </div>
  );
}
