#include "RaceGPSGeoFrame.h"
#include <iostream>
#include <iomanip>
int main()
{
    char Mode;
    double A, B, C, D;
    std::cout << std::setprecision(17);
    while (std::cin >> Mode)
    {
        RaceGPSGeoFrame::Point P{};
        if (Mode == 'l' && (std::cin >> A >> B >> C)) P = RaceGPSGeoFrame::ToUnreal(A, B, C);
        else if (Mode == 'g' && (std::cin >> A >> B >> C >> D)) P = RaceGPSGeoFrame::FromGeographic(A, B, C, D);
        else if (Mode == 'e' && (std::cin >> A >> B >> C >> D)) P = RaceGPSGeoFrame::LineEnd(A, B, C, D);
        else if (Mode == 'y' && (std::cin >> A)) { std::cout << RaceGPSGeoFrame::CompassToYaw(A) << '\n'; continue; }
        else return 2;
        std::cout << P.X << ' ' << P.Y << ' ' << P.Z << '\n';
    }
    return 0;
}
