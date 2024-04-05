target triple = "x86_64-w64-windows-gnu"
@.str = private unnamed_addr constant [4 x i8] c"\0A%d\00", align 1
@.str.1 = private unnamed_addr constant [4 x i8] c"\0A%f\00", align 1
@.str.2 = private unnamed_addr constant [3 x i8] c"%d\00", align 1
@.str.3 = private unnamed_addr constant [4 x i8] c"%lf\00", align 1
declare dso_local i32 @printf(ptr noundef, ...) #1
declare dso_local i32 @scanf(ptr noundef, ...) #1
define dso_local i32 @main() #0 {
	%1 = alloca double
	store double 7.1, ptr %1
	%2 = load double, ptr %1
	%3 = fcmp ogt double %2, 6.67
	%4 = icmp eq i1 %3, 1
	br i1 %4, label %case1_0, label %continue1_0
continue1_0:
	br label %default1
case1_0:
	store double 1.0, ptr %1
	br label %switchend1
default1:
	store double 5.0, ptr %1
	br label %switchend1
switchend1:
	%5 = load double, ptr %1
	%6 = call i32 (ptr, ...) @printf(ptr noundef @.str.1, double noundef %5)
	ret i32 0
}