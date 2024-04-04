; ModuleID = 'mylang.ll'
source_filename = "mylang.ll"
target triple = "x86_64-w64-windows-gnu"

@.str = private unnamed_addr constant [4 x i8] c"\0A%d\00", align 1
@.str.1 = private unnamed_addr constant [4 x i8] c"\0A%f\00", align 1
@.str.2 = private unnamed_addr constant [3 x i8] c"%d\00", align 1
@.str.3 = private unnamed_addr constant [4 x i8] c"%lf\00", align 1

declare dso_local i32 @printf(ptr noundef, ...)

declare dso_local i32 @scanf(ptr noundef, ...)

define dso_local i32 @main() {
  %1 = alloca i32, align 4
  store i32 3, ptr %1, align 4
  %2 = load i32, ptr %1, align 4
  %3 = call i32 (ptr, ...) @printf(ptr noundef @.str, i32 noundef %2)
  ret i32 0
}
