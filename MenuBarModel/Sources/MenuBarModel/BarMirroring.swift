//
//  BarMirroring.swift
//  Project: Thaw
//
//  Copyright (Thaw) © 2026 Toni Förster
//  Licensed under the GNU GPLv3

import Foundation

/// Which status-item owners one menu bar draws but another does not.
///
/// macOS 27 mirrors most items to every display, but some legacy custom-view
/// items stay only on the active bar. Comparing owner sets is enough to name
/// the apps a display is missing without asking each app.
public enum BarMirroring {
    /// Owners in `active` that `target` lacks. PID 0 is the agent's own
    /// placeholder for a child that is leaving, not an app.
    public static func missingOwners(active: Set<pid_t>, target: Set<pid_t>) -> Set<pid_t> {
        active.subtracting(target).subtracting([0])
    }
}
