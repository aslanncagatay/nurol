import Table from "@/app/ui/departments/table";
import { CreateDepartment } from "@/app/ui/departments/buttons";
import { lusitana } from "@/app/ui/fonts";
import { DepartmentsTableSkeleton } from "@/app/ui/skeletons";
import { Suspense } from "react";
import { Metadata } from "next";
import { getDepartments } from "../lib/api/departments";

export const metadata: Metadata = {
  title: "Departments",
};

export default async function Page() {
  const departments = await getDepartments();

  return (
    <div className="w-full">
      <div className="flex w-full items-center justify-between">
        <h1 className={`${lusitana.className} text-2xl`}>Departments</h1>
      </div>
      <div className="mt-4 flex items-center justify-end gap-2 md:mt-8">
        <CreateDepartment />
      </div>
      <Suspense key={"departments"} fallback={<DepartmentsTableSkeleton />}>
        <Table departments={departments} />
      </Suspense>
    </div>
  );
}
