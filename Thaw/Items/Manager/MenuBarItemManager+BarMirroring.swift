//
//  MenuBarItemManager+BarMirroring.swift
//  Project: Thaw
//
//  Copyright (Thaw) © 2026 Toni Förster
//  Licensed under the GNU GPLv3

import AppKit
import MenuBarModel
import ThawAXCore

@MainActor
extension MenuBarItemManager {
    /// Visible items the richest bar draws but `screen`'s bar does not.
    ///
    /// macOS 27 leaves some legacy status items (WeChat, the input menu, some
    /// calendar apps) off a secondary bar. Reading every MenuBarAgent window
    /// names them, so the Thaw Bar can offer them on the display missing them.
    /// The richest bar is the reference because it carries the full set; the
    /// active bar may itself be the short one.
    func itemsMissing(on screen: NSScreen) -> [MenuBarItem] {
        guard let bars = AXPrimitives.menuBarAgentBars(), let targetBar = MenuBarAgentWindow.bar(for: CGDisplayBounds(screen.displayID), among: bars), let referenceBar = bars.max(by: { $0.entries.count < $1.entries.count }), referenceBar.frame != targetBar.frame
        else {
            return []
        }
        let activeOwners = Set(referenceBar.entries.lazy.filter { $0.frame.width > 0 && $0.frame.height > 0 }.map(\.ownerPID))
        let targetOwners = Set(targetBar.entries.lazy.filter { $0.frame.width > 0 && $0.frame.height > 0 }.map(\.ownerPID))
        let missingOwners = BarMirroring.missingOwners(active: activeOwners, target: targetOwners)
        guard !missingOwners.isEmpty else { return [] }
        let items = itemCache.managedItems(for: .visible).filter { item in
            !item.isControlItem
                && !item.isSystemClone
                && !item.isNativeOverflowControl
                && missingOwners.contains(item.ownerPID)
        }
        itemsMissingOnBarTags.formUnion(items.map(\.tag))
        return items
    }
}
