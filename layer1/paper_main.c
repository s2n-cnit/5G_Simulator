#include <sys/stat.h>
#include <sys/types.h>
#include <stdio.h>
#include <assert.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>


void process(int x, int y)
{
	//return;
	char appendx[5];
	char appendy[5];
	int z = 0;
	char name[20] = "./ue_x";
	sprintf(appendx, "%d", x);
	strcat(name, appendx);
	strcat(name, "_y");
	sprintf(appendy, "%d", y);
	strcat(name, appendy);
	printf("Make dir: %s\n\n", name);
	int result = mkdir(name, 0777);

	char command[30] = "python3 test.py ";
	strcat(command, appendx);
	strcat(command, " ");
	strcat(command, appendy);
	strcat(command, " 0");
	printf("%s\n\n", command);
	int status = system(command);

	sleep(10);

	char moveCommand[30] = "mv bs_* ";
	strcat(moveCommand, name);
	printf("%s\n\n", moveCommand);
	int status2 = system(moveCommand);
}



void main()
{
	int i, j;

	j = 1;
	for (i = 1; i <= 25; i += 2)
	{
		//printf("(%d, %d)\n", i, j);
		process(i, j);
	}
	//printf("---------------------------\n");
	i = 25;
	//for (j = 3; j <= 27; j += 2)
	//{
	//	//printf("(%d, %d)\n", i, j);
	//	process(i, j);
	//}
	////printf("---------------------------\n");
	//j = 27;
	//for (i = 25; i <= 47; i += 2)
	//{
	//	//printf("(%d, %d)\n", i, j);
	//	process(i, j);
	//}
	////printf("---------------------------\n");
	//i = 47;
	//for (j = 29; j <= 51; j += 2)
	//{
	//	//printf("(%d, %d)\n", i, j);
	//	process(i, j);
	//}
	////printf("---------------------------\n");

	//j = 51;
	//for (i = 49; i <= 99; i += 2)
	//{
	//	//printf("(%d, %d)\n", i, j);
	//	process(i, j);
	//}
	////printf("---------------------------\n");
	//i = 99;
	//for (j = 53; j <= 79; j += 2)
	//{
	//	//printf("(%d, %d)\n", i, j);
	//	process(i, j);
	//}
	////printf("---------------------------\n");
	//j = 79;
	//for (i = 97; i >= 71; i -= 2)
	//{
	//	//printf("(%d, %d)\n", i, j);
	//	process(i, j);
	//}
	////printf("---------------------------\n");
	//i = 71;
	//for (j = 81; j <= 99; j += 2)
	//{
	//	//printf("(%d, %d)\n", i, j);
	//	process(i, j);
	//}
	////printf("---------------------------\n");
	//j = 99;
	//for (i = 69; i >= 33; i -= 2)
	//{
	//	//printf("(%d, %d)\n", i, j);
	//	process(i, j);
	//}
	////printf("---------------------------\n");
	//i = 33;
	//for (j = 97; j >= 61; j -= 2)
	//{
	//	//printf("(%d, %d)\n", i, j);
	//	process(i, j);
	//}
	////printf("---------------------------\n");
	//i = 31;
	//j = 63;
	//for (i = 31; i >= 19; i -= 2, j += 2)
	//{
	//	//printf("(%d, %d)\n", i, j);
	//	process(i, j);
	//}
	////printf("---------------------------\n");
	//i = 17;
	//j = 73;
	//for (i = 17; i >= 1; i -= 2, j -= 2)
	//{
	//	//printf("(%d, %d)\n", i, j);
	//	process(i, j);
	//}
	////printf("---------------------------\n");
	//i = 1;
	//for (j = 55; j >= 1; j -= 2)
	//{
	//	//printf("(%d, %d)\n", i, j);
	//	process(i, j);
	//}
}




