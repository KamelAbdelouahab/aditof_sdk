#ifndef SYSTEM_H
#define SYSTEM_H

#include "sdk_exports.h"
#include "status_definitions.h"

#include <memory>
#include <vector>

class SystemImpl;

namespace aditof {

class Camera;

/**
 * @class System
 * @brief The TOF system that manages the cameras. Only one instance can exist.
 */
class SDK_API System {
  private:
    System();

  public:
    ~System();
    System(const System &) = delete;
    System &operator=(const System &) = delete;
    System(System &&) = delete;
    System &operator=(System &&) = delete;

    /**
     * @brief Retrieves the one and only instance.
     * @return System&
     */
    static System &instance();

  public:
    /**
     * @brief Initializes the system. Detects available TOF cameras.
     * @return Status
     */
    Status initialize();

    /**
     * @brief Populates the given list with Camera objects that correspond to
     * the available cameras.
     * @param[out] cameraList - A container to be set with the available cameras
     * @return Status
     */
    Status
    getCameraList(std::vector<std::shared_ptr<Camera>> &cameraList) const;

  private:
    std::unique_ptr<SystemImpl> m_impl;
};

} // namespace aditof

#endif // SYSTEM_H
