import { notFound } from "next/navigation";
import { Metadata } from "next";
import { getDepartmentWithEmployees } from "@/app/lib/api/departments";
import { Suspense } from "react";
import { ReturnBack } from "@/app/ui/departments/buttons";
import { lusitana } from "@/app/ui/fonts";
import { EmployeesTableSkeleton } from "@/app/ui/skeletons";
import { DepartmentWithEmployeesTable } from "@/app/ui/departments/table";

export const metadata: Metadata = {
  title: "Department With Employees",
};

export default async function Page({ params }: { params: { id: string } }) {
  const id = params.id;
  const department = await getDepartmentWithEmployees(id);

  if (!department) {
    notFound();
  }

  return (
    <div className="w-full">
      <div className="flex w-full items-center justify-between">
        <h1 className={`${lusitana.className} text-2xl`}>
          Department With Employees
        </h1>
      </div>
      <div className="mt-4 flex items-center justify-start gap-2 md:mt-8">
        <ReturnBack />
      </div>
      <Suspense key={"employees"} fallback={<EmployeesTableSkeleton />}>
        <DepartmentWithEmployeesTable employees={department.employees || []} />
      </Suspense>
    </div>
  );
}
