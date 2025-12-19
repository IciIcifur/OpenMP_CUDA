#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

int main(const int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s nthreads npoints\n", argv[0]);
        return 1;
    }

    int nthreads = atoi(argv[1]);
    int npoints  = atoi(argv[2]);

    if (nthreads <= 0 || npoints <= 0) {
        fprintf(stderr, "nthreads and npoints must be positive\n");
        return 1;
    }

    omp_set_num_threads(nthreads);

    const int max_iter = 1000;
    const double xmin = -2.0, xmax = 1.0;
    const double ymin = -1.5, ymax = 1.5;

    // File Title
    printf("x,y\n");

    const double t_start = omp_get_wtime();

    #pragma omp parallel for collapse(2) schedule(static)
    for (int i = 0; i < npoints; ++i) {
        for (int j = 0; j < npoints; ++j) {
            double x = xmin + (xmax - xmin) * i / (npoints - 1);
            double y = ymin + (ymax - ymin) * j / (npoints - 1);

            double zx = 0.0, zy = 0.0;
            int iter = 0;

            while (zx * zx + zy * zy < 4.0 && iter < max_iter) {
                double zx_new = zx * zx - zy * zy + x;
                double zy_new = 2.0 * zx * zy + y;
                zx = zx_new;
                zy = zy_new;
                ++iter;
            }

            if (iter == max_iter) {
                #pragma omp critical
                {
                    printf("%.10f,%.10f\n", x, y);
                }
            }
        }
    }

    const double t_end = omp_get_wtime();
    const double elapsed = t_end - t_start;

    fprintf(stderr, "TIME_SECONDS=%.6f\n", elapsed);

    return 0;
}