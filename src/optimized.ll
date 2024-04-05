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
  %1 = alloca double, align 8
  store double 7.100000e+00, ptr %1, align 8
  %2 = load double, ptr %1, align 8
  %3 = fcmp ogt double %2, 6.670000e+00
  %4 = icmp eq i1 %3, true
  br i1 %4, label %case1_0, label %continue1_0

continue1_0:                                      ; preds = %0
  br label %default1

case1_0:                                          ; preds = %0
  store double 1.000000e+00, ptr %1, align 8
  br label %switchend1

default1:                                         ; preds = %continue1_0
  store double 5.000000e+00, ptr %1, align 8
  br label %switchend1

switchend1:                                       ; preds = %default1, %case1_0
  %5 = load double, ptr %1, align 8
  %6 = call i32 (ptr, ...) @printf(ptr noundef @.str.1, double noundef %5)
  ret i32 0
}
